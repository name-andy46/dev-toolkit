# Task rules: admission, and placement in `current_tasks.md`

**One skill adds to `current_tasks.md`**: `cleanup-daily-note`, in the evening
prune. `update-daily-note` may tick and update items that already exist, but
never adds one — the tasks it opens are staged in the daily note's
`## ⏭ To Carry Forward` section, under `###` headings naming their intended
destination, and migrated that evening.

That split is why this document has two parts, and they have different owners:

- **PLACEMENT — where an item goes (rules 1–5, plus the dedupe gate).**
  `cleanup-daily-note` only. It decides where a migrated item lands in a file
  that has been growing all week. `update-daily-note` reads rules 1 and 3 too,
  since that is how a Carry Forward heading is named, but never files under them.
- **ADMISSION — what may be written at all (rules 6–7).** *Both* skills, at both
  stages. It decides whether a thing is a task at all. `update-daily-note`
  applies it when staging into Carry Forward, in the session that knows;
  `cleanup-daily-note` applies it to anything reaching it by another route.

ADMISSION lives here rather than inside either skill because two copies drift,
and a test applied differently at the two stages would let observations into the
file by whichever route was laxer.

These rules exist because "just append it" produces a file that drifts into
date-named tail sections, the same project scattered across a dozen headings,
and the same task duplicated with different wording. Follow them exactly.

## PLACEMENT — Where an item goes
*(`cleanup-daily-note` only, at migration time)*

1. **Top-level headings are projects, never dates.** A heading is the durable
   name of a repo, service, ticket, or feature area — `# widget-service`,
   `# PROJ-118 — null id on CSV export`, `# PostHog Feature Flags`. Never create
   a heading like `# July 14 Carry Forward`. A project heading is permanent and
   accumulates work over time; a date heading is created once and orphaned.

2. **The date rides the item, not the heading.** Tag each item with its origin
   date: `` `(MM-DD)` `` at the end. That preserves provenance without
   fragmenting the file.

3. **Sub-headings within a project are by area, not date.** If a project grows
   past ~8 items, split it with `## ` sub-headings for *areas of work*
   (`## Console`, `## Metrics`, `## Security`) — never `## 2026-07-16`.

4. **Order within a section is by priority, not arrival.** Date-critical and
   blocking items go at the top of their section.

5. **Never append to the bottom of the file** as a default. The bottom is only
   correct when you are genuinely creating a new project heading.

## ADMISSION — What may be written at all
*(both skills: `update-daily-note` when staging, `cleanup-daily-note` when filing)*

6. **An item is the action plus the minimum context needed to start it** — about
   40 words. This enforces the vault's own rule (see "How items leave
   `current_tasks.md`" in the vault's `CLAUDE.md`): detail belongs in the daily
   log and the topic note, and an entry here only has to carry enough to
   recognise the work and find it again. Evidence, counts, command output,
   verification results and reasoning do not belong here — they go in the daily
   log or the topic note, and the item links to them. If you cannot state the
   item in 40 words, the excess is not task, it is record.

7. **Only write things with an action and a doer.** Status ("eleven machines
   remain hidden"), reference facts ("the retention window starts at T"), and warnings
   ("don't confuse these two totals") are not tasks — a checkbox on them can
   never be satisfied, so they sit open forever. Status goes in the section
   preamble, reference facts in the topic note, durable gotchas in `06_Memory/`.

   The same test applies to anything you *discovered* while working: a finding
   surfaced while working an item is not automatically a new item. Record it in
   the daily log. Promote it only if it needs a decision or an action that
   nothing else will force. Closing one item should not routinely open two.

   **Where rule 7 is applied matters.** For anything a work session surfaced,
   it is applied at Carry Forward time by `update-daily-note` — the session that
   did the work is the only one that can tell a task from something it merely
   noticed. `cleanup-daily-note` should honour that judgment rather than
   re-running the test cold on an already-staged item; it applies rule 7 itself
   to items that arrive by other routes (Top Priorities, hand-written
   checkboxes), where no warm judgment was ever made.

## The dedupe gate
*(`cleanup-daily-note` only — part of PLACEMENT)*

**Do not write an item until you have read the target section** and checked
whether an equivalent task is already there. Equivalent means *same underlying
action*, even when the wording differs — "Deploy console stack with the
widget-rotation fix" and "Deploy the console stack for the muted filter" are one
deploy, not two.

- **If a match exists: MERGE.** Keep the *clearer* description and extend the
  date tag — `` `(07-16, 07-20, 07-23)` ``. Do not add a second copy. A merge
  must never produce an item longer than the longer of its two inputs. If both
  carry detail, keep the action here and move the detail to the topic note.
- **If the merge isn't obvious** (they look related but might be genuinely
  separate work), present both to the user and ask before combining.
- **If the item is already done**, don't write it. Record the completion instead
  — in the daily log if it isn't already there.

This gate is why `cleanup-daily-note` must read `current_tasks.md` in **full**
before writing, not just the tail: both the heading match and the dedupe check
depend on knowing every existing heading and item.

`update-daily-note` reads the file in full as well — to know what it may tick,
and to copy the correct heading into Carry Forward — but it does not run this
gate. Staging a near-duplicate is harmless because the gate catches it a few
hours later; that is precisely the case it was written for, and it is also how
two chunks of the same day get reconciled into one item.

Two things follow for staged items, and both belong to the evening:

- **The date tag is the daily note's date, not the day the prune runs.** These
  differ on a backdated cleanup, and the note's date is the correct provenance.
- **A staged task may have been completed after it was staged.** Check Done
  Today before filing; if it was finished, record the completion and don't file
  the task.
