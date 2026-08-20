---
name: update-daily-note
description: Appends a session summary to the daily work log in notes/01_Logs/YYYY/MM_MonthName/, and reconciles current_tasks.md against the work just done — ticking the items it closed and filing the ones it genuinely opened, while the session still has the context to tell a task from an observation. Use this skill whenever the user wants to update their daily note, log their session, wrap up their day, end a session, capture progress, record what was done, or check off what a chunk of work finished. Triggers on phrases like "update my daily note", "log my session", "wrap up", "end session", "update my log", "save my progress", "what did we do today", "tick off what we did", "I've finished X", or any request to record the current session's work. Also use when the user says something like "I'm done for now" or "let's close out". Run it after each meaningful chunk of work, not only at day's end.
---

# Update Daily Note

Record the current session's work in two places: append a terse summary to today's daily note at `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` (e.g., `notes/01_Logs/2026/03_March/2026-03-21.md`), and reconcile `notes/current_tasks.md` against what the work actually did.

## Run this after each chunk, not just at day's end

Both halves of this skill answer the same two questions — *what did this work finish?* and *what's still open?* — so they run as one pass, against one set of live context. That context is the whole point: whether an item is done, and whether a loose end is a real task or just something you noticed, is only reliably knowable in the session that did the work. `cleanup-daily-note` runs cold in the evening and can only read the text of a line.

The log half is append-only and safe to run repeatedly, so running this several times a day costs nothing and gives a more granular Work Stream. If it only gets run once at day's end, that still works — it's one larger reconcile, still warm.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Prerequisite

Check whether today's note exists by **reading** `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` with the Read tool. A read error means it doesn't exist — invoke the `create-daily-note` skill first, then continue with the update. Use Read rather than a shell `ls`: it behaves identically on Windows, macOS, and Linux, and when the file does exist you already have its contents.

Check `notes/current_tasks.md` the same way. If it's missing, do the log half and say the task half was skipped — don't create it here; `cleanup-daily-note` owns that on the first evening prune. If it exists, read it in **full** before writing: both the heading match and the dedupe gate depend on knowing every existing heading and item.

Then read `$SKILL/../../references/task-placement-rules.md`. Rules 1–5 decide where an item goes, rules 6–7 decide whether it may be written at all, and the dedupe gate decides new-item-vs-merge. `cleanup-daily-note` applies the identical rules — that shared rulebook is what keeps the file coherent with two writers.

## Gather session data

Pull from every available source to build a complete picture of the session:

1. **Conversation context** — review what was discussed, built, debugged, or decided in this session. This is your richest source.
2. **Git activity** — run:
   - `git log --since="midnight" --oneline` for today's commits
   - `git diff --stat` for uncommitted changes
   - `git branch --show-current` for branch context
3. **Errors and resolutions** — any errors encountered during the session and how they were resolved.

## What to write

Generate terse bullet points for these sections. Think commit messages, not prose. Include commit hashes, file paths, error codes, and PR/issue references where relevant.

### Work Stream (The "Sensor")

The raw technical log of the session. Capture:
- Commands run and their outcomes (especially non-obvious ones)
- Error codes and fixes attempted/applied
- Links to PRs, docs, or external resources referenced
- Key realizations or insights ("aha!" moments)
- Files and modules touched, with brief context

Format: `- <short description> — <context/detail>`

### Done Today

Items completed during this session, as checked-off checkboxes:
- `- [x] <what was completed>`

### To Carry Forward

**Don't write task checkboxes here.** Unfinished work goes straight into `current_tasks.md` in the reconcile below, where the placement and dedupe rules apply. Leave a single italic pointer line naming where the items went — the same pattern `cleanup-daily-note` uses — so the day's note records the hand-off without duplicating the task list:

```markdown
*3 items filed to `current_tasks.md` → # widget-service, # PROJ-88 — checkout regression*
```

This is the one section whose behaviour changed. Previously every loose end became a `- [ ]` here and was migrated to `current_tasks.md` that evening by a reader who couldn't tell a task from an observation. Now it faces rule 7 at the moment it's written, by the session that knows.

### Top Priorities (suggestions only)

If the session revealed clear priorities, suggest 1-2 items. Prefix with "(suggested)" so the user can tell these apart from items they wrote themselves:
- `- [ ] (suggested) <priority item>`

A suggestion must pass rule 7 like anything else — it needs an action and a doer. "Widget throughput looks low" is an observation; put it in Work Stream. "Profile widget_handler throughput" is a priority.

Do not touch **Meetings & Syncs** or **Evening Prune** — those are for the user to fill in.

## How to append

This document is shared between the user, this skill, and possibly other sessions throughout the day. Treat it as append-only:

1. Read the current file content.
2. For each section to update, locate the section header by its emoji prefix:
   - `## 🎯 Top Priorities`
   - `## 🛠 Work Stream`
   - `## ✅ Done Today`
   - `## ⏭ To Carry Forward`
3. Find the end of that section's content — the line just before the next `## ` header or `---` separator.
4. Insert your new bullet points at that position.
5. If the section already has content, add a blank line before your new entries to visually separate them from previous content.

Never modify, reorder, or remove existing lines. If the user wrote something in a section, your entries go after theirs. The user trusts that their edits will persist exactly as written.

**This append-only guarantee covers the daily log only.** The reconcile below deliberately modifies `current_tasks.md` — ticking an item rewrites its line. That's the one file this skill is allowed to edit in place, and only in the ways described.

## Reconcile `current_tasks.md`

Same session data, same two judgments, now applied to the task file.

### First, establish what the chunk actually did

Before touching the file, state to yourself what this work completed, what it advanced but didn't finish, and what it surfaced. Be concrete — "merged the fix on branch X, commit `abc1234`", not "worked on the fix".

Where you can verify cheaply, verify: the commit exists, the file says what you think it says, the deploy landed. **Warm context makes you confident, not correct** — you remember intending things you didn't finish.

### Tick what this work completed

Scan `current_tasks.md` for open items this work actually closed. For each:

- **Mark it `- [x]` and rewrite the text to say what happened**, not what was planned: `- [x] Deployed PROJ-231 to staging — 08-07, prod still pending`.
- **Never strike through.** `- ~~struck~~` without a checkbox reads as done to a human and as open to the evening sweep, so it never leaves the file. The vault's `CLAUDE.md` ("How items leave `current_tasks.md`") is explicit on this.
- **Leave the ticked item in place.** Don't sweep it out — that's `cleanup-daily-note`'s Step 2, which files it under the correct day. Because you also wrote it to Done Today in the same pass, that sweep will correctly find it already recorded and simply drop the duplicate.

**Partial progress is not a tick.** If the work advanced an item without closing it, update its text to reflect the new state and leave it open. A three-environment deploy with one environment done is an edit, not a tick. Ticking something "basically done" is how work disappears.

**Only tick what you can name the evidence for.** If you can't say what closed it, leave it open and say why in your report.

### File what it genuinely opened

For each loose end, apply rule 7 first — **does it have an action and a doer?**

- **Yes** → place it per rules 1–5, run the dedupe gate, write it tagged with today's `` `(MM-DD)` `` date.
- **No** → it's status, a reference fact, a warning, or a finding. Don't file it. It's already captured in Work Stream; name it in your report and where it belongs if it's durable (topic note, `06_Memory/`).

Rule 7's second paragraph matters most here, because this is the moment it gets violated: a finding surfaced while working an item is not automatically a new item. Promote it only if it needs a decision or an action that nothing else will force. **Closing one item should not routinely open two.**

If an item belongs to no existing project and isn't worth a new heading, ask rather than inventing a home for it.

## Report

State plainly:

- **Ticked** — each item, with the evidence that closed it.
- **Updated** — items advanced but still open, and what changed.
- **Filed** — new items, under which heading, and any merge into an existing item.
- **Not filed** — what you declined to write as a task and where it belongs instead. This is the most useful line in the report: it's the user's chance to overrule a judgment call only you had the context to make.

Never present an inferred completion as a verified one. An item you *think* the work closed and an item you *watched* it close are different claims, and only the second justifies a tick. If unsure, leave it open and ask — an item wrongly left open costs one line; an item wrongly ticked disappears into the evening sweep and out of the file.

If the balance is off — several items filed and none ticked — say so. A reconcile that only adds is one that isn't working.

## Example output

A session's additions to the daily note:

```markdown
## 🎯 Top Priorities
- [ ] (suggested) Add unit tests for widget_handler.py

## 🛠 Work Stream (The "Sensor")
- Fixed null check in widget_handler.py — widget_id was None for empty payloads
- Debugged queue visibility timeout — batch size 10→1 (commit abc1234)
- Confirmed the staging queue drains at 400/s — measured, not a task
- Ref: PR #42 for PROJ-101

## ✅ Done Today
- [x] PROJ-101: handle widgets with missing identifiers
- [x] Raised PR #42

## ⏭ To Carry Forward (Evening Cleanup)
*2 items filed to `current_tasks.md` → # widget-service*
```

…and the matching reconcile of `current_tasks.md`:

```markdown
# widget-service
- [x] **PROJ-101: handle widgets with missing identifiers** — fixed the null check,
      merged `abc1234`, PR #42 raised `(03-14)`
- [ ] Roll the queue batch-size change to staging and prod — dev done 03-21,
      two environments left `(03-19, 03-21)`
- [ ] Write unit tests for widget_handler `(03-21)`
```

And the report back to the user:

```
Ticked 1: PROJ-101 — merged abc1234, PR #42 raised.
Updated 1: queue batch-size rollout — dev done, staging/prod still open (not a tick).
Filed 1: unit tests for widget_handler → # widget-service.
Not filed: "staging queue drains at 400/s" — a measurement, not a task.
  It's in Work Stream; say the word if you want it in the topic note.
```
