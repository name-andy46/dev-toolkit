# git-guardrails

Stops Claude from making destructive or off-policy git changes. It ships **no skills** —
installing it adds `PreToolUse` hooks that inspect git commands (on the `Bash` tool) and edits to
repository internals (on the `Write`/`Edit` tools) *before* they run, and block the dangerous ones.

It restricts **the agent's** actions only. Git commands you run yourself in a terminal are
untouched.

If you're new to git, this is the plugin that stops the handful of commands that lose work you
can't get back — and stops a credential reaching a public repo, which is the mistake that's
hardest to undo.

## Requirements

**Python 3.8 or newer, on your `PATH` as `python3`.** No other dependencies — standard library
only, no `jq`, no bash, so it works the same on macOS, Linux, and Windows.

> **Windows note.** Some Python installers provide only `python.exe`, not `python3.exe`. If
> `python3 --version` doesn't work in your terminal, the hook can't run — and a hook that can't
> run silently allows everything. Install Python from the Microsoft Store (which provides
> `python3`), or run the self-test below to confirm the guardrails are actually live.

## Verify it's working (30 seconds)

A guardrail you *assume* is active is worse than none. Confirm it, in a throwaway directory where
nothing can be lost:

```bash
mkdir guardrail-test && cd guardrail-test && git init
```

Then ask Claude:

> run git reset --hard in this directory

You should see the tool call refused with a message beginning `[git-guardrails] BLOCKED:`. If the
command runs instead, the hook isn't loading — check `python3 --version`, and that you started a
new session after installing.

## What it blocks

**Git commands** (`PreToolUse` on the `Bash` tool):

1. **Force pushes.** Any `git push --force` / `-f` / `+refspec` is blocked — it rewrites remote
   history. The safer `--force-with-lease` is also blocked by default (set
   `GIT_GUARD_ALLOW_FORCE_WITH_LEASE=1` to permit it).
2. **Hard resets.** `git reset --hard` is blocked — it silently discards uncommitted work and can
   rewind the branch. Soft and mixed resets are fine.
3. **Working-tree wipes.** `git clean -f…` is blocked (it deletes untracked files irreversibly). A
   dry run (`git clean -n` / `--dry-run`) is allowed.
4. **Remote deletion of a protected branch.** Deleting a **remote** branch (`git push --delete`,
   `git push origin :branch`) is blocked when the target is protected. **Local** deletion
   (`git branch -d/-D`) is *not* blocked — a local branch is private and recoverable from the
   reflog, so blocking it just gets in the way of cleanup.
5. **Writes/pushes to a protected branch — off by default.** Committing, merging, rebasing, and
   pushing to a *protected* branch (default `^(main|master|develop)$|^release/`). This is the one
   rule that's **disabled** out of the box, because working solo on your own project means
   committing to `main` all day and that's perfectly correct. Turn it on with
   `GIT_GUARD_ENFORCE_BRANCH_SCOPE=1` when you join a team or start using pull requests. With it
   on, the agent judges the *effective* branch, so `git switch -c my-feature && git commit …` is
   fine while `git commit` on `main` is blocked.

**Repository internals** (both the `Write`/`Edit` tools and the `Bash` tool):

6. **`.git/` hand-edits.** Writing to any path under a `.git/` directory is blocked — this stops
   the agent tampering with refs or `.git/config`, or dropping a `.git/hooks/` script that would
   bypass the rules above. Caught on two surfaces: (a) a `Write`/`Edit`/`MultiEdit` call whose path
   is under `.git/`, and (b) a `Bash` command that writes or deletes a `.git/` path by shell means
   — redirection (`echo … > .git/HEAD`), `tee`, `dd`, `truncate`, `sed -i`, `rm`. Plain **reads**
   (`cat`/`grep .git/…`) are left alone. It does **not** affect `git commit`, `git add`, etc.:
   those write `.git/` from inside the `git` subprocess, which isn't a tool call the hook can see.
   Only the agent *hand-editing* `.git/` is stopped.

7. **Secrets in a push.** A `git push` is blocked when its **outgoing** commits (those not yet on
   any remote) add a recognised credential signature — Atlassian tokens (`ATATT…`/`ATCTT…`), AWS
   keys (`AKIA…`), private-key blocks, Slack (`xox…`), GitHub (`gh?_…`). It scans **committed
   content only** (untracked files are never pushed) and fails **open** if the outgoing range
   can't be computed. Extend the signatures with `GIT_GUARD_SECRET_PATTERNS`. The matched value is
   never echoed — only the offending commit is named.

When something is blocked, the reason goes to both Claude and you, so the agent can correct course.

## ⚠️ A guardrail, not a hard boundary

This gates the agent's tool calls by parsing command strings and file paths heuristically. It stops
**naive and accidental** damage; it is not a defense against a determined bypass. Obfuscating the
command so the flag never appears literally (`F=--force; git push $F`), a shell or git alias, or an
`sh -c` with an encoded payload will all get through.

**It matches commands, not mentions of commands.** A rule only fires where the command *starts a
shell segment* — the beginning of the command line, or after `;`, `&&`, `||`, `|`, or a newline
(optionally behind `sudo` or `env VAR=x`). So writing documentation, grepping for a phrase, or
naming a command in a commit message is not treated as running it:

```bash
echo "never run git push --force on main"     # allowed
grep -rn "git reset --hard" docs/             # allowed
git commit -m "document git reset --hard"     # allowed
cd repo && git push --force origin main       # BLOCKED — a real invocation
```

Flags are read from the segment carrying the subcommand, so `git commit -m "avoid --force" && git
push origin feature` is allowed rather than being read as a force push. The cost of anchoring is a
slightly wider bypass surface — `xargs git push --force` and `sh -c "git push -f"` go unseen — which
falls in the same determined-bypass category as the cases above. One residual: a heredoc body whose
*line* begins with a dangerous command (a fenced code block in a tutorial you're writing) still
looks like command position and will be blocked.

Rule 6 closes the `.git/` hole on both surfaces, but `cp`/`mv`/`ln` into `.git/` are deliberately
**not** matched. Copying a file *onto* `.git/` internals is only ever intentional — squarely the
determined-bypass case — and `install`/`rsync`/`python -c` would stay open regardless, so covering
`cp`/`mv` would imply a protection level this can't actually provide.

One accepted edge in rule 5: a *bare* `git push` chained after a non-protected explicit push in the
same command — `git push origin feature && git push` while sitting on a protected branch — isn't
re-checked against the current branch. A lone `git push` on a protected branch is still blocked,
and any *explicit* push to a protected branch is caught wherever it sits in a compound command.

**Installing this plugin means it runs a script on every Bash and Write/Edit tool call, at your
user privilege level, with no per-run prompt** — that is how all plugin hooks work. That's why it
lives in its own plugin: opting into these guardrails is a separate, explicit install, never a side
effect of installing something for its skills.

## Configuration

All optional, set as environment variables — in your shell profile, or the `env` block of
`~/.claude/settings.json`:

| Variable | Default | Effect |
|---|---|---|
| `GIT_GUARD_PROTECTED_BRANCHES` | `^(main\|master\|develop)$\|^release/` | Regex matching protected branch names. Core names are end-anchored so `maintenance`/`development` stay writable; `release/` is a prefix, so `release/2.8` is protected. |
| `GIT_GUARD_ENFORCE_BRANCH_SCOPE` | `0` | Set `1` to enable the protected-branch write/push rule (rule 5). |
| `GIT_GUARD_BLOCK_FORCE_PUSH` | `1` | Set `0` to disable force-push blocking (rule 1). |
| `GIT_GUARD_ALLOW_FORCE_WITH_LEASE` | `0` | Set `1` to permit `git push --force-with-lease`. |
| `GIT_GUARD_BLOCK_HARD_RESET` | `1` | Set `0` to allow `git reset --hard` (rule 2). |
| `GIT_GUARD_BLOCK_CLEAN` | `1` | Set `0` to allow `git clean -f` (rule 3). |
| `GIT_GUARD_PROTECT_BRANCH_DELETION` | `1` | Set `0` to allow remote deletion of protected branches (rule 4). |
| `GIT_GUARD_PROTECT_GIT_DIR` | `1` | Set `0` to allow writes to `.git/` (rule 6). |
| `GIT_GUARD_BLOCK_PUSH_SECRETS` | `1` | Set `0` to disable the pre-push secret scan (rule 7). |
| `GIT_GUARD_SECRET_PATTERNS` | *(none)* | Extra regex (`\|`-joined) appended to the built-in secret signatures in rule 7. |

## Install

```bash
claude plugin install git-guardrails@dev-toolkit
```

Start a new Claude Code session for the hook to take effect, then run the self-test above.
