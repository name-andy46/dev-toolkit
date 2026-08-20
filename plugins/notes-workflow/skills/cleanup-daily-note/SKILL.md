---
name: cleanup-daily-note
description: Performs cleanup on a daily work log — moves unfinished tasks to current_tasks.md under project headings, consolidates completed items into Done Today, prunes the task-file sections it wrote to (compressing over-long items and demoting non-tasks, proposing stale ones for deletion), and flags noise for deletion while preserving signals. Cleans today's note by default, or a specific past date when one is given (backdated cleanups are normal). Use this skill whenever the user wants to clean up a daily note, do an evening prune, end their day, tidy their log, or review what to keep vs discard. Triggers on phrases like "cleanup my daily note", "evening cleanup", "prune my notes", "end of day cleanup", "tidy my log", "clean up today's note", "clean up the note for the 15th", or any request to organize and prune a daily work log.
---

# Cleanup Daily Note

Perform an evening cleanup on today's daily note at `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md`. This is the "signal vs noise" pass — consolidating completed work, migrating unfinished tasks, and flagging clutter for the user to review.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Which day to clean up

This skill accepts an **optional date argument** naming which daily note to clean up:

- **No argument** → clean up **today's** note (the evening-prune default).
- **A date or day reference** (e.g. `2026-07-15`, "the 15th", "yesterday's note") → clean up **that** note. Resolve it to a concrete `YYYY-MM-DD` and use it everywhere below in place of "today".

**Backdated cleanups are normal and expected.** In practice these notes often get cleaned up a few days after the fact, in a batch — do not assume the target date is today, and never silently substitute today's date for the requested one. When a cleanup is backdated, Step 2 (consolidate completed items) is frequently a no-op: by the end of that day the completed work was already sitting in Done Today, so there is usually nothing left to move. That is fine — say so and move on; the load-bearing step on a backdated note is task **migration** (Step 1).

## Prerequisites

Resolve the target date first (see "Which day to clean up"). Then read that day's note at `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` with the Read tool (e.g. `notes/01_Logs/2026/07_July/2026-07-15.md`) — you need its contents anyway. If Read errors, the note doesn't exist: tell the user and stop, there's nothing to clean up.

Also read `notes/current_tasks.md`. If Read errors, it doesn't exist yet: copy this plugin's `vault-template/current_tasks.md` into the vault — that's the shipped starter, so a file created here matches what a fresh vault gets.

### Cleaning up a day that isn't today

When the target date isn't today (see "Which day to clean up"), it's a retrospective prune — run the same steps, but:

- Say plainly in your summary that the note is N days old, so they know it isn't today's.
- Expect some items to be **already resolved** since that day. Before migrating an item, check whether it has since been done (it may already be tracked in `current_tasks.md`, or a later daily log may record it landing). Don't migrate stale work: mark it superseded in place with a one-line note on what actually happened, and migrate only what's genuinely still open.

## Placement rules for `current_tasks.md`

**Read `$SKILL/../../references/task-placement-rules.md` before writing anything
to `current_tasks.md`.** It carries the seven placement rules (where an item
goes, and what may be written at all) plus the dedupe gate, and is shared with
`update-daily-note` so both skills govern the file identically. Steps 1 and 3
below assume you have read it.

## Step 1: Move unfinished tasks to current_tasks.md

Scan the entire daily note for unchecked checkboxes (`- [ ]`). Items prefixed
with `(suggested)` count too — they were raised during the session and never
acted on, so they're still open.

Ignore empty placeholder checkboxes (a bare `- [ ]` with no text). Those are
template scaffolding, not tasks — replace with a plain `-` or drop the line.

For each real task, do **not** blindly append. Place it:

**1. Identify the project.** Infer it from the item itself — the repo or
service it touches, its ticket key, or its feature area. If an item belongs to
no existing project and isn't worth a new heading, it's probably a stray
thought rather than a task; ask the user rather than inventing a home for it.

**2. Find or create the heading.** Read the existing `# ` headings in
`current_tasks.md` *before* writing anything. Match the item to an existing
heading if one fits. Only create a new `# <Project>` heading when none does,
and name it per placement rules 1 and 3.

**3. Apply the admission test and the dedupe gate** from the reference —
rules 6 and 7 decide whether it belongs in the file at all, and the dedupe gate
decides whether it's a new item or a merge into an existing one. Both are hard
gates. An item that fails rule 7 here is usually one you can't judge cold; when
in doubt, ask rather than filing an observation as a task.

**4. Append under the heading**, tagged with its origin date per rule 2.

**5. Delete it from the daily note**, leaving a single italic pointer line in
the Carry Forward section naming where the items went — so the day's note still
records that the work was handed off, without duplicating the task list.

## Step 2: Consolidate completed items into Done Today

Move checked checkboxes (`- [x]`) from these specific sections into the `## ✅ Done Today` section:

- **Top Priorities** (`## 🎯 Top Priorities`) — move `- [x]` items to Done Today, delete from Top Priorities
- **Carry Forward** (`## ⏭ To Carry Forward`) — move `- [x]` items to Done Today, delete from Carry Forward
- **current_tasks.md** (`notes/current_tasks.md`) — move `- [x]` items to Done Today in the daily note, delete from current_tasks.md

Do **not** move checked items from Work Stream (`## 🛠 Work Stream`). That section is a raw technical log and its checked items are part of the narrative record.

On a **backdated** cleanup this step is usually a no-op (the day's completed items are already in Done Today) — confirm there's nothing to move and continue.

When adding items to Done Today, append them after any existing content in that section (same append-only pattern as the update-daily-note skill).

If a completed item in `current_tasks.md` carries detail the daily note's
version lacks (the reasoning, a revisit trigger, a decision's rationale), fold
that detail into the Done Today entry rather than letting it die with the
deleted line. The task file loses the item; the log should keep the knowledge.

## Step 3: Prune the sections you touched

Steps 1 and 2 only ever *add* to `current_tasks.md` or remove what someone
already ticked. Nothing re-reads an item once it's written, so an item overtaken
by events sits open indefinitely. This step is that read-back.

For every `current_tasks.md` section you wrote to this pass, re-read its **open**
items and:

- **Compress** any past the ~40-word cap (placement rule 6), moving the detail to
  the topic note or the daily log and leaving a link. Do this yourself — nothing
  is lost, the text only moves.
- **Demote** any that are status, reference fact, or warning rather than action
  (placement rule 7) — into the section preamble, the topic note, or
  `06_Memory/`. Also yours to do, for the same reason.
- **Propose deletions** for any item overtaken by events. Verify before
  proposing — check the repo, git history, or the system of record rather than
  assuming — and say what you checked. **Do not delete open items on your own
  authority**: list them with your evidence and let the user decide, the same way
  Step 4 handles noise. Compressing and demoting are lossless; deleting is not.

Scope this to sections **this pass already wrote to**. A section the evening
never touched stays untouched — sweeping the whole file is a separate,
user-initiated job, not part of the evening prune.

Report the counts: items compressed, demoted, and proposed for deletion.

## Step 4: Flag noise for user review

Read through the Work Stream section and identify content that matches the "noise" patterns below. Do not delete anything automatically — present a summary to the user and let them decide what to remove.

### What counts as noise

- **Failed experiments**: Multiple attempts where only the last one worked. Example: three broken `curl` commands before the fourth succeeded — the first three are noise.
- **Transitory logs**: Long stack traces or verbose terminal output. The error message and fix are signal; the bulk of the raw log is noise.
- **Administrative friction**: Notes like "Waiting for IT to reset my password" or "Slack was down for 10 minutes" — no future technical value.
- **Duplicate links**: The same URL or ticket link pasted multiple times.
- **Restated conclusions**: A line that repeats a decision already stated earlier in the same section. Compress it into the original rather than deleting outright — the restatement sometimes carries a detail the first mention didn't.

### What counts as signal (keep these)

- **The "why"**: Reasoning behind decisions — "Switched to Library B because Library A doesn't support concurrency in Go 1.21."
- **Working snippets**: The exact SQL query, regex, or command that solved the problem.
- **Decision logic**: "Team decided to use Sidecar pattern for logging to reduce latency."
- **People references**: "Spoke to Sarah from DevOps; she's the lead for the K8s migration."
- **Analytical honesty**: A recorded refusal to over-claim ("2 data points can't separate 'getting worse' from 'seeing more'"), a rejected alternative and why, or a note that a verification step was skipped and what was relied on instead. This reads like hedging but is high-value — it's what stops a future session from re-deriving a conclusion that was already examined and set aside.

A dense technical log with no noise in it is a normal outcome. Do not
manufacture removal candidates to show effort — if the section is all signal,
say so and move on.

### How to present noise suggestions

Show the user a numbered list of items you think are noise, with brief reasoning:

```
I found a few items in Work Stream that look like noise:

1. Lines 24-27: Three failed curl commands before the working one on line 28 — keep only the working version?
2. Line 35: "Waiting for VPN to reconnect" — administrative friction, no technical value.
3. Lines 41-58: Full stack trace — the error message on line 41 and fix on line 60 capture the signal.

Want me to remove any of these? (e.g., "remove 1 and 2", "remove all", "skip")
```

Wait for the user's response before deleting anything. If the user says "skip" or doesn't want to remove anything, move on.

## Step 5: Check off the Evening Prune checklist

The daily note has an Evening Prune section (`## 🧹 Evening Prune`) with a checklist. As you complete each step, check off the corresponding item:

- `- [x] **Delete Noise**` — after the user confirms noise removal (or skips)
- `- [x] **Highlight Signals**` — after reviewing and preserving signals in Work Stream
- `- [x] **Task Migration**` — after moving unfinished tasks to `current_tasks.md`
- `- [x] **Link People/Services**` — check this off if people/service references were already linked, or note if any are missing

Append a short clause to each item saying what that pass actually found ("none
found; all decision-reasoning", "3 items → # widget-service"). A bare `- [x]`
records only that the step ran; the clause records the result, which is what
makes the prune auditable later.

## Order of operations

Run the steps in this order to avoid conflicts:

1. Resolve the target date, then read both files (`notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` and `notes/current_tasks.md`) — use `ls` via Bash to verify existence first. Read `current_tasks.md` in **full**, not just the tail — Step 1's dedupe gate and heading match both depend on knowing every existing heading and item.
2. Step 2 first — consolidate completed items (moves from current_tasks.md and daily note sections into Done Today)
3. Step 1 — move unfinished tasks to current_tasks.md
4. Step 3 — prune the sections Step 1 just wrote to (compress/demote yourself; deletions are proposed, not applied)
5. Step 4 — flag noise for review (interactive, waits for user)
6. Step 5 — check off Evening Prune items
7. Confirm to the user what was done

This order matters twice over. Step 2 pulls completed items from current_tasks.md before Step 1 pushes new unfinished items into it — avoids accidentally moving items that were just added. And Step 3 runs *after* Step 1, because "the sections you touched" isn't known until Step 1 has finished writing.

## Example workflow

```
Cleanup summary for 2026-03-17:

✅ Moved to Done Today (from Top Priorities, Carry Forward, current_tasks.md):
  - [x] PROJ-101: handle widgets with missing identifiers
  - [x] Review PR #44 feedback

📋 Migrated to current_tasks.md:
  → # widget-service
    - [ ] Write unit tests for widget_handler `(03-17)`
    - [ ] (suggested) Add integration test for widget handling `(03-17)`
  → # PROJ-88 — checkout regression  (new heading)
    - [ ] Reproduce the intermittent 502 on staging `(03-17)`

  Merged 1 duplicate: "Deploy the widget stack" already existed under
  # widget-service from 03-11 → now tagged `(03-11, 03-17)` rather than listed twice.

✂️ Pruned # widget-service (the one section this pass wrote to):
  Compressed 2 items over the 40-word cap — the rollout evidence moved to
  [[widget-service-rollout]], the items now link to it.
  Demoted 1: "staging still runs the old image" is status, not action → section preamble.

  Proposed for deletion (your call — nothing removed yet):
  1. - [ ] Pin the widget-handler base image `(02-28)` — appears done: pinned in
     `Dockerfile:3` as of commit `a1b2c3d` (03-09). Checked the repo, not just the log.

🔍 Noise review:
  1. Lines 24-27: Three failed curl commands — keep only the working one?
  2. Line 35: "Waiting for VPN" — no technical value

Want me to remove any of these?
```

## Report honestly

The summary must reflect what actually happened. If you merged two items, say
which. If you couldn't tell whether an item was already done, say so rather
than guessing. If a section was left untouched because it was already clean,
say that too. A cleanup that silently drops a task is worse than one that
leaves it in place.

This applies hardest to Step 3. Say which sections you pruned and which you left
alone, and never present a deletion as verified when you only inferred it — an
item you *suspect* is done and an item you *confirmed* is done are different
claims, and only the second one justifies proposing its removal.
