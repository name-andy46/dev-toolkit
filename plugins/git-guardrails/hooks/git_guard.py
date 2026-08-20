#!/usr/bin/env python3
"""git-guardrails — PreToolUse hook that blocks the agent from destructive or
off-policy repository changes.

Wired for two matchers:

  * Bash                       — inspects the git command (rules 1-5, 6b, 7)
  * Write|Edit|MultiEdit|…     — blocks hand-edits to files under .git/ (rule 6a)

It reads the PreToolUse payload on stdin and exits 2 (with a reason on stderr)
to BLOCK, or exits 0 to allow.

  1. Force push        — `git push --force` / `-f` / `+refspec` is blocked.
                         `--force-with-lease` too, unless allowed (see below).
  2. Hard reset        — `git reset --hard` is blocked (discards work).
  3. Working-tree wipe — `git clean -f…` is blocked (deletes untracked files);
                         a dry run (`-n` / `--dry-run`) is allowed.
  4. Remote branch     — deleting a REMOTE branch (`git push --delete` /
     deletion            `git push … :refspec`) is blocked when the target is a
                         protected branch. Local `git branch -d/-D` is left
                         alone (private, recoverable via reflog).
  5. Protected-branch  — committing/merging/rebasing/resetting and PUSHING to a
     write guard         protected branch. OFF by default here: someone working
                         solo commits to main legitimately, and blocking their
                         first commit teaches nothing. Turn it on with
                         GIT_GUARD_ENFORCE_BRANCH_SCOPE=1 when you start
                         collaborating.
  6a. Write/Edit tools — a Write/Edit/MultiEdit/NotebookEdit call whose path is
                         under a .git/ directory is blocked.
  6b. Shell writes     — a Bash command that writes to / deletes a .git/ path by
                         shell means (redirection, tee, dd, truncate, sed -i,
                         rm) is blocked — the Write/Edit hook can't see a shell
                         redirect.
  7. Pre-push secret   — a `git push` whose OUTGOING commits (reachable from
     scan                HEAD but not yet on any remote) add a recognised
                         credential signature is blocked. Scans COMMITTED
                         content only — untracked files are never pushed.
                         Fail-open if the range can't be computed.

Rule 6 does NOT block `git commit`, `git add`, etc.: git writes .git/ as a
subprocess, which is not a tool call the hook sees. Only the agent editing .git/
itself is stopped (e.g. tampering with refs or planting .git/hooks/). cp/mv/ln
into .git/ is not matched (source/dest is ambiguous) and remains a documented
residual, as does obfuscating the command so no pattern matches.

This is a GUARDRAIL, not a hard boundary — it gates the agent's tool calls, so
it stops naive and accidental mistakes. It parses command strings heuristically
and can be bypassed on purpose (encoding the command, aliases, `sh -c` with an
obfuscated payload).

Config (environment variables, all optional):
  GIT_GUARD_PROTECTED_BRANCHES      Regex matching protected branch names.
                                    Default: ^(main|master|develop)$|^release/
  GIT_GUARD_ENFORCE_BRANCH_SCOPE    1 to enforce rule 5, 0 to disable (default).
  GIT_GUARD_BLOCK_FORCE_PUSH        1 (default) to enforce rule 1, 0 to disable.
  GIT_GUARD_ALLOW_FORCE_WITH_LEASE  1 to permit `git push --force-with-lease`.
  GIT_GUARD_BLOCK_HARD_RESET        1 (default) to enforce rule 2, 0 to disable.
  GIT_GUARD_BLOCK_CLEAN             1 (default) to enforce rule 3, 0 to disable.
  GIT_GUARD_PROTECT_BRANCH_DELETION 1 (default) to enforce rule 4, 0 to disable.
  GIT_GUARD_PROTECT_GIT_DIR         1 (default) to enforce rule 6, 0 to disable.
  GIT_GUARD_BLOCK_PUSH_SECRETS      1 (default) to enforce rule 7, 0 to disable.
  GIT_GUARD_SECRET_PATTERNS         Optional extra regex (|-joined) appended to
                                    the built-in secret signatures.

Python 3.8+, standard library only — no jq, no bash, no shell. That matters:
the original was a bash script that parsed the payload with jq, and on a machine
without jq it failed *open*, leaving the user believing they were guarded when
they were not. See the README for the 30-second self-test.

Matching is anchored to COMMAND POSITION: a command is inspected only where it
starts a shell segment (start of string, or after `;` `&&` `||` `|` or a
newline, optionally behind `sudo` / `env VAR=x`). Mentioning a dangerous command
inside a message, a quoted string, or a document you're writing is therefore not
treated as running it — `echo "never run git push --force"` and
`grep -rn "git reset --hard" docs/` both pass. The trade-off is a slightly wider
bypass surface (`xargs git push`, `sh -c "git push -f"` go unseen), which sits
in the same already-documented "determined bypass" category. Flags are read from
the segment that carries the subcommand, so a commit message mentioning
`--force` cannot trip the push rule in a compound command.

Known residual: a heredoc body whose *line* begins with a dangerous command
(a fenced code block in a tutorial, say) still looks like command position.
"""

import json
import os
import re
import subprocess
import sys

# --- config -----------------------------------------------------------------

PROTECTED_BRANCHES = os.environ.get(
    "GIT_GUARD_PROTECTED_BRANCHES", r"^(main|master|develop)$|^release/"
)
ENFORCE_BRANCH_SCOPE = os.environ.get("GIT_GUARD_ENFORCE_BRANCH_SCOPE", "0") == "1"
BLOCK_FORCE_PUSH = os.environ.get("GIT_GUARD_BLOCK_FORCE_PUSH", "1") == "1"
ALLOW_FORCE_WITH_LEASE = os.environ.get("GIT_GUARD_ALLOW_FORCE_WITH_LEASE", "0") == "1"
BLOCK_HARD_RESET = os.environ.get("GIT_GUARD_BLOCK_HARD_RESET", "1") == "1"
BLOCK_CLEAN = os.environ.get("GIT_GUARD_BLOCK_CLEAN", "1") == "1"
PROTECT_BRANCH_DELETION = os.environ.get("GIT_GUARD_PROTECT_BRANCH_DELETION", "1") == "1"
PROTECT_GIT_DIR = os.environ.get("GIT_GUARD_PROTECT_GIT_DIR", "1") == "1"
BLOCK_PUSH_SECRETS = os.environ.get("GIT_GUARD_BLOCK_PUSH_SECRETS", "1") == "1"

SECRET_RE = (
    r"ATATT[A-Za-z0-9_-]{8,}|ATCTT[A-Za-z0-9_-]{8,}|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN[A-Z ]*PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{8,}"
    r"|gh[opsu]_[A-Za-z0-9]{20,}"
)
if os.environ.get("GIT_GUARD_SECRET_PATTERNS"):
    SECRET_RE += "|" + os.environ["GIT_GUARD_SECRET_PATTERNS"]

# A shell segment's leading noise: `sudo`, `env VAR=x`, plain whitespace.
LEADING_RE = re.compile(r"^\s*(?:sudo\s+|env\s+\S+=\S+\s+)*")
# The subcommand of a segment that starts with git, allowing a few global
# options (`git -C /path push`). Anchored, so `git log --grep=push` and
# `echo "git push --force"` are not treated as invocations.
GIT_SUBCMD_RE = re.compile(r"^git\s+(?:\S+\s+){0,4}?([a-z][a-z-]*)(\s|$)")


def segments(cmd):
    """Split a command on shell separators into candidate command positions."""
    return re.split(r"[;&|\n]", cmd)


def git_calls(cmd):
    """Yield (subcommand, args_string) for each real git invocation.

    A git invocation counts only when it *starts* a shell segment — that is what
    keeps prose, commit messages, and grep patterns from being read as commands.
    """
    for seg in segments(cmd):
        body = LEADING_RE.sub("", seg)
        m = GIT_SUBCMD_RE.match(body)
        if m:
            yield m.group(1), body[m.end():]


def starts_with_cmd(seg, name):
    """Does this segment invoke `name` at command position?"""
    body = LEADING_RE.sub("", seg)
    return re.match(r"%s(\s|$)" % re.escape(name), body) is not None


def deny(reason):
    """exit 2 blocks the tool call; stderr is surfaced to Claude and the user."""
    sys.stderr.write("[git-guardrails] BLOCKED: %s\n" % reason)
    sys.exit(2)


def is_protected(branch):
    """Is this branch name protected? (normalise a refs/heads/ prefix first)"""
    b = branch[len("refs/heads/"):] if branch.startswith("refs/heads/") else branch
    return bool(b) and re.search(PROTECTED_BRANCHES, b) is not None


def has_git_push(cmd):
    return any(sub == "push" for sub, _ in git_calls(cmd))


def has_short_f(text):
    """A short flag bundle containing -f (-f, -fd, -xdf) but not long --force."""
    return re.search(r"(^|\s)-[A-Za-z]*f[A-Za-z]*(\s|$)", text) is not None


def push_arg_lists(cmd):
    """For each `git … push` segment of a compound command, the args after `push`.

    Splitting on shell separators means EVERY push in a compound command is
    inspected, not just the last. A bare `git push` yields an empty string.
    """
    return [args for sub, args in git_calls(cmd) if sub == "push"]


def push_dest_branches(cmd):
    """Destination branch of every push refspec across ALL push segments.

    Skips flags and each segment's first non-flag token (the remote name). A bare
    `git push` contributes nothing — the caller falls back to HEAD.
    """
    dests = []
    for line in push_arg_lists(cmd):
        seen_remote = False
        for tok in line.split():
            if ":" in tok:
                dests.append(tok.rsplit(":", 1)[1])  # src:dst and :dst -> dst
            elif tok.startswith("-"):
                continue
            elif not seen_remote:
                seen_remote = True
            else:
                dests.append(tok)
    return [d for d in dests if d]


def git(cwd, *args):
    """Run git, returning stdout stripped, or '' on any failure (fail open)."""
    try:
        res = subprocess.run(
            ["git", "-C", cwd or "."] + list(args),
            capture_output=True, text=True, timeout=8,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return res.stdout.strip() if res.returncode == 0 else ""


def current_branch(cwd):
    return git(cwd, "symbolic-ref", "--quiet", "--short", "HEAD")


def writes_to_git(c):
    """Shell-level writes/deletes to .git/ (rule 6b).

    Each pattern ties the .git/ path to a WRITE operator, so plain reads
    (cat/grep .git/…) are left alone. cp/mv/ln are intentionally not matched.
    """
    writers = [
        ("tee", r"\.git/"),
        ("dd", r"of=[^\s]*\.git/"),
        ("truncate", r"\.git/"),
        ("sed", r"(-i|--in-place)[^\n]*\.git/"),
        ("rm", r"(^|[\s/])\.git([\s/]|$)"),
    ]
    for seg in segments(c):
        # output redirection into a repository-internals path
        if re.search(r"""[0-9]*&?>>?\s*['"]?[^\s;|&<>]*\.git/""", seg):
            return True
        for name, tail in writers:
            if starts_with_cmd(seg, name) and re.search(tail, seg):
                return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return 0  # unparseable payload: fail open rather than wedge the session

    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or ""

    # -- rule 6a: hand-edits to .git/ via the Write/Edit family ---------------
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        if not PROTECT_GIT_DIR:
            return 0
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if not path:
            return 0
        # Normalise Windows separators so C:\repo\.git\config matches too.
        if re.search(r"(^|/)\.git(/|$)", path.replace("\\", "/")):
            deny(
                "editing files under .git/ is not allowed ('%s'). Use git commands "
                "(git config, git commit, …) instead of hand-editing repository "
                "internals." % path
            )
        return 0

    # Everything below is for the Bash tool only.
    if tool != "Bash":
        return 0

    cmd = tool_input.get("command") or ""
    if not cmd:
        return 0

    # Only inspect commands that reference git — either a `git …` invocation or a
    # path under a .git/ directory (both contain the whole word "git").
    if not re.search(r"\bgit\b", cmd):
        return 0

    # -- rule 6b: shell-level writes to .git/ ---------------------------------
    if PROTECT_GIT_DIR and writes_to_git(cmd):
        deny(
            "this command writes to or deletes .git/ internals via the shell. "
            "Repository state must go through git commands, not direct edits to .git/."
        )

    # -- rule 1: force push --------------------------------------------------
    for args in (push_arg_lists(cmd) if BLOCK_FORCE_PUSH else []):
        has_lease = re.search(r"--force-with-lease", args) is not None
        has_hard = (
            re.search(r"--force([\s=]|$)", args) is not None
            or has_short_f(args)
            or re.search(r"(^|\s)\+[A-Za-z0-9_./-]+:", args) is not None
        )
        if has_hard:
            deny(
                "force push (git push --force / -f / +refspec) rewrites remote "
                "history. If you truly need it, run it yourself outside the agent."
            )
        if has_lease and not ALLOW_FORCE_WITH_LEASE:
            deny(
                "force push (git push --force-with-lease) is blocked. Set "
                "GIT_GUARD_ALLOW_FORCE_WITH_LEASE=1 to permit the safer lease variant."
            )

    # -- rule 2: hard reset --------------------------------------------------
    if BLOCK_HARD_RESET and any(
        sub == "reset" and re.search(r"--hard([\s=]|$)", args)
        for sub, args in git_calls(cmd)
    ):
        deny(
            "git reset --hard discards uncommitted changes (and can rewind the "
            "branch). Stash or commit first, or use a soft/mixed reset."
        )

    # -- rule 3: git clean -f ------------------------------------------------
    for sub, args in (git_calls(cmd) if BLOCK_CLEAN else []):
        if sub == "clean" and not re.search(
            r"(^|\s)(-[A-Za-z]*n[A-Za-z]*|--dry-run)(\s|$)", args
        ):
            if re.search(r"--force([\s=]|$)", args) or has_short_f(args):
                deny(
                    "git clean -f deletes untracked files/directories irreversibly. "
                    "Preview with 'git clean -n' first."
                )

    # -- rule 4: remote deletion of a protected branch -----------------------
    if PROTECT_BRANCH_DELETION and has_git_push(cmd):
        for line in push_arg_lists(cmd):
            seg_del = re.search(r"(^|\s)(-[a-zA-Z]*[dD]|--delete)(\s|$)", line) is not None
            seen_remote = False
            for tok in line.split():
                if tok.startswith(":"):
                    target = tok[1:]
                    if target and is_protected(target):
                        deny(
                            "deleting remote branch '%s' is not allowed — it is "
                            "protected (%s)." % (target, PROTECTED_BRANCHES)
                        )
                    continue
                if tok.startswith("-"):
                    continue
                if seg_del:
                    if not seen_remote:
                        seen_remote = True  # first non-flag token is the remote
                    elif is_protected(tok):
                        deny(
                            "deleting remote branch '%s' is not allowed — it is "
                            "protected (%s)." % (tok, PROTECTED_BRANCHES)
                        )

    # -- rule 5: writing/pushing to a protected branch -----------------------
    if ENFORCE_BRANCH_SCOPE:
        calls = list(git_calls(cmd))
        mutators = {"commit", "merge", "rebase", "cherry-pick", "revert", "reset", "am"}
        if any(sub in mutators for sub, _ in calls):
            # Effective target: if the command switches/creates a branch, judge on
            # that (`git switch -c feature && git commit` -> feature); else HEAD.
            switches = []
            for sub, args in calls:
                if sub in ("switch", "checkout"):
                    for tok in args.split():
                        if not tok.startswith("-"):
                            switches.append(tok.strip("'\""))
                            break
            tgt = switches[-1] if switches else current_branch(cwd)
            # Undeterminable branch (detached HEAD, unborn, not a repo): fail open.
            if tgt and is_protected(tgt):
                deny(
                    "'%s' is a protected branch (%s); committing/rewriting history "
                    "here is not allowed. Work on a feature branch, e.g. "
                    "'git switch -c <topic>'." % (tgt, PROTECTED_BRANCHES)
                )

        if has_git_push(cmd):
            dests = push_dest_branches(cmd)
            if dests:
                for d in dests:
                    if is_protected(d):
                        deny(
                            "pushing to protected branch '%s' (%s) is not allowed. "
                            "Push a feature branch and open a PR instead."
                            % (d, PROTECTED_BRANCHES)
                        )
            else:
                # No explicit refspec: the push targets the current branch's upstream.
                cur = current_branch(cwd)
                if cur and is_protected(cur):
                    deny(
                        "pushing the current branch '%s' is not allowed — it is "
                        "protected (%s). Push a feature branch and open a PR instead."
                        % (cur, PROTECTED_BRANCHES)
                    )

    # -- rule 7: pre-push secret scan ----------------------------------------
    # Scans the diff of the OUTGOING commits (reachable from HEAD, not on any
    # remote). Committed content only. Fail-open if the range can't be computed.
    # The matched value is NEVER echoed — only the offending commit is named.
    if BLOCK_PUSH_SECRETS and has_git_push(cmd):
        outgoing = git(cwd, "rev-list", "HEAD", "--not", "--remotes")
        for commit in outgoing.split():
            diff = git(cwd, "show", "--no-color", "--format=", commit)
            added = "\n".join(l for l in diff.splitlines() if l.startswith("+"))
            if added and re.search(SECRET_RE, added):
                deny(
                    "push blocked — commit %s adds what looks like a secret (a "
                    "token/key signature in its diff). Remove it before pushing: "
                    "'git log -p %s' to locate it, then rewrite the commit or "
                    "'git rm --cached <file>'. (Scans committed content only; set "
                    "GIT_GUARD_BLOCK_PUSH_SECRETS=0 to override.)" % (commit, commit)
                )

    return 0


if __name__ == "__main__":
    sys.exit(main())
