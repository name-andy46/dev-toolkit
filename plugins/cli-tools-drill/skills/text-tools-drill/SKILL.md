---
name: text-tools-drill
description: Hands the user ONE real, hands-on practice problem for the Unix text-processing tools — grep, sed, awk, find/xargs, and the coreutils glue (sort/uniq/cut/wc/tr) — instead of running the search itself, then checks their solution. Use whenever the user wants to practice, drill, or be quizzed on these command-line tools: triggers on "text-tools drill", "drill me on awk/sed/grep/find", "let me practice grep", "quiz me on sed", "give me a CLI challenge", "I'll do the search this time", or any request to exercise command-line text tools. One problem per invocation (per-prompt), not a persistent session mode. Self-contained — ships with its own skill checklist; no external files required.
---

# text-tools-drill

Hand the user **one** real practice problem for the Unix pipe-filter tools — grep, sed, awk, find/xargs, and the coreutils glue — let them solve it, then verify. The whole point: instead of running a search yourself, delegate it to the user as a drill, so the skill gets exercised on real work.

**Per-prompt, not per-session.** One problem per invocation. After verifying, return to normal — do not loop or hijack the session.

**Self-contained.** Everything needed ships with this skill. The skill map lives in the bundled **`CHECKLIST.md`** next to this file. This skill does **not** require any personal notes/vault, learning-guide, or external file to run.

## Prerequisite: a POSIX shell

Every problem in this drill is a `grep`/`sed`/`awk`/`find` one-liner, so the user needs a shell
where those exist: macOS, Linux, or — on Windows — WSL, Git Bash, or MSYS2. **PowerShell and `cmd`
don't have them**; the equivalents are unrelated cmdlets (`Select-String`, `Where-Object`,
`ForEach-Object`).

If there's any doubt (the user is on Windows, or a shell command has already failed this session),
**ask once before posing the first problem.** If they don't have a POSIX shell, say so plainly and
stop — handing someone an exercise they cannot run teaches nothing. Don't silently translate the
problem into PowerShell either: that's a different toolset with a different mental model, and it
belongs in its own drill skill.

## Teaching contract (non-negotiable)

- **Never give the command or the answer up front.** Pose the *problem statement* in plain English — what we want to know — plus which tool/flag to focus on. The user writes the command.
- Show a cleaner/idiomatic form **only after** the user's attempt, never before.
- **One concept at a time**, calibrated one notch above their current comfort.
- Any destructive step (`sed -i`, overwrite, `rm`) must be **previewed first** and run on a **throwaway copy** — by both the user and by you when verifying.

## Step 1 — Calibrate (from the bundled checklist)

1. Read **`./CHECKLIST.md`** (bundled beside this file) — it holds the tool descriptions and the difficulty ladder. Pick a problem one notch above the user's current comfort.
2. Determine the user's level, in this order:
   - If the user names a tool/level ("drill me on awk", "I'm shaky on find"), honor it.
   - Else, if a progress tracker is already in play this session (see Step 5), use it.
   - Else, **ask one quick question**: which tool they want to drill, or roughly how comfortable they are — then start there. Don't assume; don't hunt for external files.

## Step 2 — Pick a REAL target in the CURRENT repo

Repo-agnostic — work with whatever repo/directory is open. **Never assume a specific repo or file layout.** Two modes, prefer (a):

**(a) Live mode — the high-value path.** If, in the current task, you were about to run a search/edit/count to make progress, convert *that actual need* into the problem statement and hand it to the user instead of running it.

**(b) Synthetic mode.** If there's no live need, cheaply inspect the current repo (a couple of `ls`/`grep` calls — no full-file reads) and synthesize a genuine problem from its real files: a real symbol to find, real config to slice, a real column to tally.

## Step 3 — Pose the problem (and stop)

State, in plain English:
- **What we want to know** (the question/outcome), grounded in a real file/path in this repo.
- **Which tool** to use and any **flag focus** (e.g. "use awk, with a `count[]` tally").
- Any **constraint** (e.g. "filenames only", "preview only — no `-i`", "exclude venv").

Then **stop and wait.** Ask the user to paste back **both the command and its output**. Do not reveal the solution.

## Step 4 — Verify (recheck if needed)

When the user pastes their command + output:
1. **Does the command produce that output?** If it's read-only and cheap, re-run it to confirm. If destructive, verify the logic on a copy — never the real file.
2. **Does it correctly answer the question?** Watch the classic traps: unscoped recursion drowning in `venv/`/`node_modules/`; glob-vs-regex confusion; BRE needing `-E`; `sed -i` with no preview; awk field/separator mistakes; `find | grep` (searches names) vs `find | xargs grep` (searches contents); `uniq` without a preceding `sort`.
3. **Feedback:** confirm what's right, name the one thing to improve, and *then* show a cleaner/idiomatic form if one exists. Keep it to one teaching point.

## Step 5 — Progress (opt-in) & close

- **No tracker by default.** The skill is stateless across sessions on purpose (users move between many repos).
- The **first time** a user clears a skill, offer once: *"Want me to keep a local progress tracker so drills can pick up where you left off?"* If yes, ask **where** to put it (they choose — a notes vault, home dir, wherever) and thereafter read/update that file to calibrate. If no, stay stateless and just give verbal feedback.
- End the round. Invite another drill when they want the next rep. Do **not** auto-loop.

## Notes

- The difficulty ladder and per-tool descriptions live in **`CHECKLIST.md`** — read it rather than duplicating it here.
- Prefer problems whose answer is checkable from the pasted output. Avoid open-ended ones.
- Keep each round to a single, well-scoped question — this is a rep, not a project.
- **Scope boundary:** stay within the pipe-filter family (grep, sed, awk, find/xargs, coreutils glue). Structured-JSON (`jq`), version-history search (`git grep`/`log -S`/`blame`), and grep variants (`rg`) are *different* mental models — out of scope for this skill; they belong in their own drill skills.
