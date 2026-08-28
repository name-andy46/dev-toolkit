---
name: update-daily-note
description: Appends a session summary to the daily work log in notes/01_Logs/YYYY/MM_MonthName/, ticks off and updates the current_tasks.md items the work touched, and stages any newly opened tasks in the day's Carry Forward section for the evening cleanup to migrate — while the session still has the context to tell a task from an observation. It never adds tasks to current_tasks.md itself. Use this skill whenever the user wants to update their daily note, log their session, wrap up their day, end a session, capture progress, record what was done, or check off what a chunk of work finished. Triggers on phrases like "update my daily note", "log my session", "wrap up", "end session", "update my log", "save my progress", "what did we do today", "tick off what we did", "I've finished X", or any request to record the current session's work. Also use when the user says something like "I'm done for now" or "let's close out". Run it after each meaningful chunk of work, not only at day's end.
---

# Update Daily Note

Append a terse summary of the current session to today's daily note at `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` (e.g., `notes/01_Logs/2026/03_March/2026-03-21.md`), reconcile the `notes/current_tasks.md` items the work touched, and stage anything it newly opened in the note's **To Carry Forward** section.

**This skill never adds a task to `current_tasks.md`.** It may tick and update items that are already there; new work is staged in Carry Forward and migrated that evening by `cleanup-daily-note`, the file's only writer.

**Run it after each chunk, not just at day's end.** Whether an item is done, and whether a loose end is a real task or just something you noticed, is only reliably knowable in the session that did the work — `cleanup-daily-note` runs cold and can only read the text of a line. The log half is append-only and safe to re-run, so several passes a day cost nothing and give a more granular Work Stream.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Prerequisite

Check whether today's note exists by **reading** `notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` with the Read tool. A read error means it doesn't exist — invoke the `create-daily-note` skill first, then continue with the update. Use Read rather than a shell `ls`: it behaves identically on Windows, macOS, and Linux, and when the file does exist you already have its contents.

Check `notes/current_tasks.md` the same way. If it's missing, do the log half, stage Carry Forward items under best-guess headings, and say there were none to match — don't create it here; `cleanup-daily-note` owns that on the first evening prune. If it exists, read it in **full**. You need every heading (to name Carry Forward destinations) and every open item (to know what to tick or update, and to avoid staging a duplicate). The tail is not enough.

Then read `$SKILL/../../references/task-placement-rules.md`. **ADMISSION** (rules 6–7) is yours — it governs what may be written into Carry Forward. **PLACEMENT** is `cleanup-daily-note`'s, but read rules 1 and 3 anyway, since that is how headings are named and you may be proposing one.

## Gather session data

1. **Conversation context** — what was discussed, built, debugged, or decided. Your richest source.
2. **Git activity** — `git log --since="midnight" --oneline`, `git diff --stat`, `git branch --show-current`.
3. **Errors and resolutions** — errors hit during the session and how they were resolved.

## What to write

Terse bullets. Think commit messages, not prose. Include commit hashes, file paths, error codes, and PR/issue references where relevant.

### Work Stream (The "Sensor")

The raw technical log of the session:
- Commands run and their outcomes (especially non-obvious ones)
- Error codes and fixes attempted/applied
- Links to PRs, docs, or external resources referenced
- Key realizations or insights ("aha!" moments), and files touched with brief context

Format: `- <short description> — <context/detail>`

### Done Today

Items completed during this session: `- [x] <what was completed>`

### To Carry Forward — this is where new tasks go

**Every task this session opens is written here, and nowhere else.** Carry Forward is the staging area; `cleanup-daily-note` migrates it that evening.

Write real checkboxes, grouped under a `###` heading naming **where the item should end up** in `current_tasks.md`:

```markdown
## ⏭ To Carry Forward (Evening Cleanup)

### # widget-service ▸ ## Console
- [ ] Run `seed_fixtures.sh` — needs the staging DB URI, blocks the PROJ-88 repro

### # PROJ-88 — checkout regression  (new heading)
- [ ] Reproduce the intermittent 502 on staging
```

**Choosing the heading.** You have read `current_tasks.md` in full, so use it:

- **Related to work already tracked there → reuse that exact heading**, verbatim, including the `## ` area sub-heading if the project has them. Write it as `# Project` or `# Project ▸ ## Area`. This is the common case.
- **Genuinely new work with no home there → name a new heading** per placement rules 1 and 3 (a durable project, repo, service, ticket or feature area — never a date) and mark it `(new heading)`.
- **No existing project fits and it isn't worth a new heading** → it is probably not a task. Apply rule 7; if it survives, ask rather than inventing a home for it.

**Apply the admission test before writing anything here.** Rules 6 and 7 govern this section exactly as they govern `current_tasks.md` — an item is the action plus ~40 words of context, and it needs an action and a doer. Status, reference facts, warnings and findings are not tasks; they belong in Work Stream, the topic note, or `06_Memory/`.

**Don't stage a duplicate.** If an equivalent item already exists in `current_tasks.md`, tick or update it in place instead. And no date tags here — the note *is* the date, and the evening pass tags each item with the note's date, which stays correct on a backdated prune.

### Top Priorities (suggestions only)

If the session revealed clear priorities, suggest 1–2, prefixed so the user can tell them from their own:
- `- [ ] (suggested) <priority item>`

A suggestion must pass rule 7 too — it needs an action and a doer. "Widget throughput looks low" is an observation; put it in Work Stream. "Profile widget_handler throughput" is a priority.

Do not touch **Meetings & Syncs** or **Evening Prune** — those are the user's.

## How to append

The daily note is shared between the user, this skill, and possibly other sessions. Treat it as append-only:

1. Read the current file content.
2. Locate the section header by its emoji prefix — `## 🎯 Top Priorities`, `## 🛠 Work Stream`, `## ✅ Done Today`, `## ⏭ To Carry Forward`.
3. Insert at the end of that section's content — just before the next `## ` header or `---` separator — with a blank line first if the section already has content.

Never modify, reorder, or remove existing lines. If the user wrote something in a section, your entries go after theirs. In Carry Forward, if a `###` heading you need is already present from an earlier chunk, append under it rather than opening a second copy.

**This append-only guarantee covers the daily log only.** The reconcile below deliberately rewrites lines in `current_tasks.md`.

## What this skill may do to `current_tasks.md`

**Read it in full. Tick what the work closed. Update what it changed. Add nothing.**

| Allowed | Not allowed |
|---|---|
| Tick an existing item and rewrite its line to say what happened | Add a new item |
| Update an existing open item's text to reflect its new state | Create a new heading |
| | Delete, sweep, or reorder anything |

New work goes to Carry Forward. `cleanup-daily-note` is the only skill that adds to `current_tasks.md`, plus the user on direct instruction.

The split follows the two questions rather than the two skills. Deciding *whether a loose end is a task* needs warm context, so it happens here. Deciding *where a new item goes in a file that grows all week* — the heading match, the dedupe gate, the ordering — needs a cold read of the whole file, so it happens once, in the evening, by one writer. Reconciling an item that already exists needs neither: you know what you just did to it.

## Reconcile

### First, establish what the chunk actually did

Before touching the file, state to yourself what this work completed, what it advanced but didn't finish, and what it surfaced. Be concrete — "merged the fix on branch X, commit `abc1234`", not "worked on the fix".

Where you can verify cheaply, verify: the commit exists, the file says what you think it says, the deploy landed. **Warm context makes you confident, not correct** — you remember intending things you didn't finish.

### Tick what this work completed

For each open item this work actually closed:

- **Mark it `- [x]` and rewrite the text to say what happened**, not what was planned: `- [x] Deployed PROJ-231 to staging — 08-07, prod still pending`.
- **Never strike through.** `- ~~struck~~` without a checkbox reads as done to a human and as open to the evening sweep, so it never leaves the file. The vault's `CLAUDE.md` ("How items leave `current_tasks.md`") is explicit on this.
- **Leave the ticked item in place.** Sweeping it out is `cleanup-daily-note`'s Step 2, which files it under the correct day. Because you also wrote it to Done Today in the same pass, that sweep will find it already recorded and drop the duplicate.

**Only tick what you can name the evidence for.** If you can't say what closed it, leave it open and say why in your report.

### Update what this work advanced

**Partial progress is not a tick.** A three-environment deploy with one environment done is an update, not a tick. Rewrite the item's text to reflect the new state, leave it `- [ ]`, and extend its date tag: `` `(03-19, 03-21)` ``.

Keep the item inside rule 6's ~40 words: an update *replaces* state, it does not accumulate it. If the new state needs more explaining, that goes in Work Stream and the item points at it. Ticking something "basically done" is how work disappears — updating is the honest alternative, and it is why this skill still touches the file at all.

### Stage what it genuinely opened

For each loose end, apply rule 7 — **does it have an action and a doer?**

- **Yes** → write it to **Carry Forward**, under the matching heading. Not into `current_tasks.md`.
- **No** → it's status, a reference fact, a warning, or a finding. Don't stage it. It's already in Work Stream; name it in your report, and where it belongs if it's durable (topic note, `06_Memory/`).

Rule 7's second paragraph matters most here, because this is where it gets violated: a finding surfaced while working an item is not automatically a new item. Promote it only if it needs a decision or an action that nothing else will force. **Closing one item should not routinely open two.**

## Report

- **Ticked** — each item, with the evidence that closed it.
- **Updated** — items advanced but still open, and what changed in the line.
- **Staged** — new items written to Carry Forward, and the heading each is destined for. Say which headings are new.
- **Not staged** — what you declined to write as a task and where it belongs instead. The most useful line in the report: the user's chance to overrule a judgment call only you had the context to make.

Never present an inferred completion as a verified one. An item you *think* the work closed and an item you *watched* it close are different claims, and only the second justifies a tick. If unsure, leave it open and ask — an item wrongly left open costs one line; an item wrongly ticked disappears into the evening sweep and out of the file.

If the balance is off — several items staged and none ticked or updated — say so. A reconcile that only adds is one that isn't working.

## Example output

A session's additions to the daily note:

```markdown
## 🎯 Top Priorities
- [ ] (suggested) Add unit tests for widget_handler.py

## 🛠 Work Stream (The "Sensor")
- Fixed null check in widget_handler.py — widget_id was None for empty payloads
- Debugged queue visibility timeout — batch size 10→1 (commit abc1234)
- Confirmed the staging queue drains at 400/s — measured, not a task

## ✅ Done Today
- [x] PROJ-101: handle widgets with missing identifiers
- [x] Raised PR #42

## ⏭ To Carry Forward (Evening Cleanup)

### # widget-service
- [ ] Write unit tests for widget_handler
```

…and `current_tasks.md` — one tick, one update, nothing added:

```markdown
# widget-service
- [x] **PROJ-101: handle widgets with missing identifiers** — fixed the null check,
      merged `abc1234`, PR #42 raised `(03-14)`
- [ ] Roll the queue batch-size change to staging and prod — dev done,
      two environments left `(03-19, 03-21)`
```

The unit-test task was **not** added here — it's staged in Carry Forward for the evening.

And the report back to the user:

```
Ticked 1: PROJ-101 — merged abc1234, PR #42 raised.
Updated 1: queue batch-size rollout — dev done, staging/prod left. Not a tick.
Staged 1: unit tests for widget_handler → # widget-service (existing heading).
Not staged: "staging queue drains at 400/s" — a measurement, not a task.
  It's in Work Stream; say the word if you want it in the topic note.
```
