---
name: cleanup-daily-note
description: Performs cleanup on a daily work log — migrates the tasks staged in the note's Carry Forward section (plus any other loose checkboxes) into current_tasks.md under project headings, as the single skill permitted to add to that file, consolidates completed items into Done Today, prunes the task-file sections it wrote to (compressing over-long items and demoting non-tasks, proposing stale ones for deletion), and flags noise for deletion while preserving signals. Cleans today's note by default, or a specific past date when one is given (backdated cleanups are normal). Use this skill whenever the user wants to clean up a daily note, do an evening prune, end their day, tidy their log, or review what to keep vs discard. Triggers on phrases like "cleanup my daily note", "evening cleanup", "prune my notes", "end of day cleanup", "tidy my log", "clean up today's note", "clean up the note for the 15th", or any request to organize and prune a daily work log.
---

# Cleanup Daily Note

Perform an evening cleanup on a daily note at `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md`. This is the "signal vs noise" pass — consolidating completed work, migrating unfinished tasks, and flagging clutter for the user to review.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Which day to clean up

Takes an **optional date argument**: no argument → **today's** note; a date or day reference (`2026-07-15`, "the 15th", "yesterday's note") → **that** note, resolved to a concrete `YYYY-MM-DD` and used everywhere below in place of "today".

**Backdated cleanups are normal and expected** — these notes often get cleaned in a batch days later. Never silently substitute today's date for the requested one. On a backdated prune:

- Say in your summary that the note is N days old.
- **Step 2 is usually a no-op** — that day's completed work is already in Done Today. Fine; say so and move on. The load-bearing step is task migration (Step 1).
- **Expect some items to have been resolved since.** Before migrating, check whether it has since been done — `current_tasks.md` may already track it, or a later daily log may record it landing. Don't migrate stale work: mark it superseded in place with a one-line note on what actually happened, and migrate only what's genuinely still open.

## Prerequisites

Resolve the target date first. Then read that day's note at `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` with the Read tool (e.g. `notes/01_Logs/2026/07_July/2026-07-15.md`) — you need its contents anyway. If Read errors, the note doesn't exist: tell the user and stop, there's nothing to clean up.

Also read `notes/current_tasks.md`. If Read errors, it doesn't exist yet: copy this plugin's `vault-template/current_tasks.md` into the vault — that's the shipped starter, so a file created here matches what a fresh vault gets.

## You are the only skill that adds

This skill is the only one that **adds** items or headings to `current_tasks.md`. `update-daily-note` may tick and update items that already exist, but never adds one — every new item it opens is staged in the daily note's Carry Forward section for you to migrate in Step 1. The user may of course edit the file directly, or instruct you to write to it outside a prune.

That is what the placement rules depend on: one pass, reading the whole file once, can keep headings coherent and catch duplicates; several warm sessions appending through the day cannot. Reconciling an item that already exists needs no such view, which is why ticking and updating stay warm.

**Read `$SKILL/../../references/task-placement-rules.md` before writing anything to `current_tasks.md`.** ADMISSION (rules 6–7) is shared with `update-daily-note`, which applies it when staging. PLACEMENT (rules 1–5 and the dedupe gate) is yours alone. Steps 1 and 3 assume you have read both.

## Step 1: Move unfinished tasks to current_tasks.md

Items reach this step by two routes, and they need different handling.

### Route A: the Carry Forward section (the normal route)

`update-daily-note` stages tasks in `## ⏭ To Carry Forward` as it works, grouped under `###` headings naming their intended destination:

```markdown
### # widget-service ▸ ## Console
- [ ] Run `seed_fixtures.sh` — needs the staging DB URI, blocks the PROJ-88 repro

### # PROJ-88 — checkout regression  (new heading)
- [ ] Reproduce the intermittent 502 on staging
```

These already passed the admission test in the session that wrote them, by someone who knew whether the loose end was a task or a passing observation. **Honour the proposed heading by default** — don't re-litigate rule 7 on a warm judgment because you'd have called it differently cold. Your job is the placement work needing the whole file in view, plus the checks only the evening can make:

1. **Resolve the heading.** If it exists, use it verbatim. If marked `(new heading)`, confirm nothing equivalent appeared during the day, then create it per rules 1 and 3. If the proposed heading no longer fits — the project got split into areas since, say — place it correctly and say so.
2. **Run the dedupe gate.** The check that genuinely needs the evening: two chunks of one day can stage the same work in different words. Merge per the gate, extending the date tag.
3. **Check it isn't already done.** A task staged at 11:00 may have been finished at 16:00 — look in Done Today and `current_tasks.md` first. If done, don't file it; record the completion instead.
4. **Apply rule 6** — compress anything past the ~40-word cap as you file it.
5. **Tag with the note's date** per rule 2 — *not* today's. On a backdated prune these differ, and the note's date is the correct provenance.

**Override a staged item only with a reason you can state**, and put it in the report. The warm judgment is usually the better one; when you disagree and it isn't clear-cut, ask.

### Route B: loose checkboxes elsewhere in the note

Scan the rest of the note for unchecked checkboxes (`- [ ]`) — Top Priorities most often, including `(suggested)` items, plus anything the user hand-wrote. These carry no proposed destination, so place them from scratch:

1. **Identify the project** from the item itself — the repo or service it touches, its ticket key, its feature area. If it belongs to no existing project and isn't worth a new heading, it's probably a stray thought; ask rather than inventing a home for it.
2. **Find or create the heading.** Match an existing `# ` heading if one fits; only create a new one when none does, named per rules 1 and 3.
3. **Apply the admission test and the dedupe gate.** Both are hard gates. An item failing rule 7 here is usually one you can't judge cold — when in doubt, ask rather than filing an observation as a task.
4. **Append under the heading**, tagged with the note's date per rule 2.

Ignore empty placeholder checkboxes (a bare `- [ ]` with no text) — template scaffolding, not tasks. Replace with a plain `-` or drop the line.

### Then clear the section

Once everything is filed, **delete the migrated items and their `###` headings** from Carry Forward, leaving a single italic pointer line naming where they went:

```markdown
*3 items filed to `current_tasks.md` → # widget-service ▸ ## Console (2),
# PROJ-88 — checkout regression (1, new heading). 1 staged item dropped — completed later the same day.*
```

Leave anything you did **not** migrate where it is, and say why. An unmigrated item silently deleted is the one outcome this step must never produce.

## Step 2: Consolidate completed items into Done Today

Move checked checkboxes (`- [x]`) into `## ✅ Done Today` from:

- **Top Priorities** (`## 🎯 Top Priorities`) — move, then delete from there.
- **Carry Forward** (`## ⏭ To Carry Forward`) — move, then delete. A staged task finished later the same day shows up here; it belongs in Done Today, not in `current_tasks.md`. Drop its `###` heading too if that empties it.
- **`notes/current_tasks.md`** — move into Done Today in the daily note, delete from the task file.

Do **not** move checked items from Work Stream (`## 🛠 Work Stream`) — that's a raw technical log and its checked items are part of the narrative record.

Append to Done Today after any existing content (same append-only pattern as `update-daily-note`). If a completed item in `current_tasks.md` carries detail the daily note's version lacks — the reasoning, a revisit trigger, a decision's rationale — fold it into the Done Today entry rather than letting it die with the deleted line. The task file loses the item; the log should keep the knowledge.

## Step 3: Prune the sections you touched

Steps 1 and 2 only ever *add* to `current_tasks.md` or remove what someone already ticked. Nothing re-reads an item once written, so an item overtaken by events sits open indefinitely. This step is that read-back.

For every section you wrote to this pass, re-read its **open** items and:

- **Compress** any past the ~40-word cap (rule 6), moving the detail to the topic note or daily log and leaving a link. Do this yourself — nothing is lost, the text only moves.
- **Demote** any that are status, reference fact, or warning rather than action (rule 7) — into the section preamble, the topic note, or `06_Memory/`. Also yours, for the same reason.
- **Propose deletions** for any item overtaken by events. Verify before proposing — check the repo, git history, or the system of record rather than assuming — and say what you checked. **Never delete an open item on your own authority**: list it with your evidence and let the user decide. Compressing and demoting are lossless; deleting is not.

Scope this to sections **this pass already wrote to**. A section the evening never touched stays untouched — sweeping the whole file is a separate, user-initiated job.

Report the counts: compressed, demoted, proposed for deletion.

## Step 4: Flag noise for user review

Read the Work Stream section and identify content matching the patterns below. Delete nothing automatically — present a summary and let the user decide.

**Noise:**
- **Failed experiments** — several attempts where only the last worked; the first three broken `curl` commands are noise.
- **Transitory logs** — long stack traces or verbose output. The error message and the fix are signal; the bulk of the log is not.
- **Administrative friction** — "Waiting for IT to reset my password", "chat was down for 10 minutes" — no future technical value.
- **Duplicate links** — the same URL or ticket pasted repeatedly.
- **Restated conclusions** — a line repeating a decision already stated in the same section. Compress into the original rather than deleting; the restatement sometimes carries a detail the first mention didn't.

**Signal (keep):**
- **The "why"** — "Switched to Library B because Library A doesn't support concurrency in Go 1.21."
- **Working snippets** — the exact SQL, regex, or command that solved it.
- **Decision logic** — "Team chose the Sidecar pattern for logging to reduce latency."
- **People references** — "Spoke to Sarah from DevOps; she's the lead for the K8s migration."
- **Analytical honesty** — a refusal to over-claim ("2 data points can't separate 'getting worse' from 'seeing more'"), a rejected alternative and why, or a note that a verification step was skipped and what was relied on instead. Reads like hedging, but it's what stops a future session re-deriving a dead end.

A dense technical log with no noise in it is a normal outcome. Don't manufacture removal candidates to show effort — if it's all signal, say so and move on.

Present candidates as a numbered list with brief reasoning ("Lines 24–27: three failed curl commands before the working one on line 28 — keep only that?"), then **wait for the user's response** before deleting anything. "Skip" is a valid answer.

## Step 5: Check off the Evening Prune checklist

The note's `## 🧹 Evening Prune` checklist gets ticked as you go: **Delete Noise** (after the user confirms or skips), **Highlight Signals** (after reviewing Work Stream), **Task Migration** (after Step 1), **Link People/Services** (if references are linked, or note which are missing).

Append a short clause to each saying what that pass found — "none found; all decision-reasoning", "3 items → # widget-service". A bare `- [x]` records only that the step ran; the clause records the result, which is what makes the prune auditable later.

## Order of operations

1. Resolve the target date, then read both files — Read is the existence check, and it hands you the contents in the same call. Read `current_tasks.md` in **full**, not just the tail: Step 1's dedupe gate and heading match depend on knowing every existing heading and item.
2. **Step 2** — consolidate completed items.
3. **Step 1** — migrate unfinished tasks.
4. **Step 3** — prune the sections Step 1 wrote to.
5. **Step 4** — flag noise (interactive, waits for the user).
6. **Step 5** — check off Evening Prune.
7. Confirm what was done.

This order matters three times over. Step 2 pulls completed items out of `current_tasks.md` before Step 1 pushes new ones in, so nothing just-added gets swept. Step 2 also clears any *staged* task finished later that day out of Carry Forward, so Step 1 never files work already done. And Step 3 runs after Step 1, because "the sections you touched" isn't known until Step 1 has written.

## Example workflow

```
Cleanup summary for 2026-03-17:

✅ Moved to Done Today: PROJ-101 (widgets with missing identifiers), Review PR #44 feedback

📋 Migrated to current_tasks.md:
  From Carry Forward (headings honoured):
  → # widget-service            - [ ] Write unit tests for widget_handler `(03-17)`
  → # PROJ-88 — checkout regression  (new heading, as proposed)
                                - [ ] Reproduce the intermittent 502 on staging `(03-17)`
  From Top Priorities (no staged destination, placed here):
  → # widget-service            - [ ] (suggested) Add integration test `(03-17)`

  Merged 1: staged "Roll the batch-size change to staging and prod" matched an open
  item under # widget-service from 03-11 → now `(03-11, 03-17)`, not listed twice.
  Dropped 1: "Review PR #44 feedback" was staged at 11:00, completed at 16:00 —
  it's in Done Today, so it was not filed.

✂️ Pruned # widget-service (the one section this pass wrote to):
  Compressed 2 over the 40-word cap — rollout evidence → [[widget-service-rollout]].
  Demoted 1: "staging still runs the old image" is status, not action → preamble.
  Proposed for deletion (your call — nothing removed):
  1. - [ ] Pin the widget-handler base image `(02-28)` — appears done: pinned in
     `Dockerfile:3` as of `a1b2c3d` (03-09). Checked the repo, not just the log.

🔍 Noise review:
  1. Lines 24-27: three failed curl commands — keep only the working one?
  2. Line 35: "Waiting for VPN" — no technical value
  Want me to remove any of these?
```

## Report honestly

The summary must reflect what actually happened: say which items you merged, say when you couldn't tell whether something was already done rather than guessing, and say when a section was left alone because it was already clean. A cleanup that silently drops a task is worse than one that leaves it in place.

This applies hardest to Step 3. Say which sections you pruned and which you left alone, and never present a deletion as verified when you only inferred it — an item you *suspect* is done and one you *confirmed* is done are different claims, and only the second justifies proposing its removal.
