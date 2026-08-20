# notes-workflow

Claude's persistent memory for your own working knowledge — the time-based context that spans
every project you touch: what you're doing, where you left off, who you're waiting on, and the
facts and decisions you want to remember. It belongs to *you*, not to any one codebase.

The approach balances the messy reality of a working day — captured continuously in a **daily
log** (the "sensor") — against a single clean **command center** (`current_tasks.md`) that always
tells you what's next. The skills below automate the lifecycle so the vault stays current without
manual bookkeeping.

The vault is plain markdown files in a folder. Claude reads and writes them directly — nothing to
sync, nothing proprietary. [Obsidian](https://obsidian.md) makes browsing nicer by following the
`[[links]]` between notes, but it's entirely optional.

## Getting started

**There's no setup.** Install the plugin, restart your session, and ask for something:

> create today's note

If you don't have a vault yet, the skill offers to create one at `~/notes` (or anywhere else you
name), seeded from this plugin's [`vault-template/`](vault-template) — the folder structure, the
conventions file, blank note templates, and a `START_HERE.md` tour. Then it carries on with what
you asked for.

### Configuration

| Variable | Purpose |
| --- | --- |
| `NOTES_PATH` | Absolute path to your vault. Optional — only needed if your vault isn't at `~/notes` or a `notes/` folder in your working directory. |

Set it in your shell profile (`~/.bashrc`, `~/.zshrc`, …) if you keep your vault somewhere else,
such as a synced Dropbox or iCloud folder:

```bash
export NOTES_PATH="$HOME/Dropbox/my-notes"
```

The full resolution order — and what happens when nothing is found — is in
[`references/vault-resolution.md`](references/vault-resolution.md).

### Optional: make the vault authoritative everywhere

The skills below trigger on their own phrasings, but Claude only treats the vault as the *first*
place to look for project context once it knows the vault exists. If you want that behavior in
every session, add a short pointer to your user-scope `~/.claude/CLAUDE.md`:

````markdown
## Notes vault

A markdown notes vault is the authoritative home for my project context and captured memory:
daily logs, a `current_tasks.md` command center, per-topic working notes, and topic memories
under `06_Memory/`. On any recall/status/resume question, search it before any repo-wide scan,
and route durable facts into it rather than losing them to the session.

**Locating it:** `$NOTES_PATH` → else a `notes/` directory under the working directory → else
`~/notes`. Once located, the vault's own `CLAUDE.md` is the source of truth for its conventions.
````

Keep it minimal — the detail lives in the vault's own `CLAUDE.md`, so this block stays stable as
your conventions grow.

## Personal memory vs. team memory

This vault is for **your** knowledge. Anything the whole team relies on — how a specific system
behaves, why an architectural call was made — belongs wherever your team already keeps its docs
(a repo's `docs/`, a wiki), not here. Go by ownership:

- *Your own working context, or a fact you want Claude to remember later* → **this vault**.
- *Your team needs it, and one project clearly owns it* → **that project's** docs.
- *It spans several projects, so nothing owns it* → **this vault**, then published by hand to
  wherever your team reads.

The agent-facing version of these rules — including the split between Claude Code's always-loaded
memory and this vault's `06_Memory/` — lives in the vault's own `CLAUDE.md`. This section is the
human-facing orientation; that file is what Claude follows.

## Vault structure

Kept deliberately minimal so it stays easy to scan (and cheap to search):

| Path | What it holds |
|---|---|
| `START_HERE.md` | Plain-English tour of the vault, for a first-time user. |
| `01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` | Daily logs — the "sensor" for errors, snippets, and progress. |
| `02_Meetings/` | One note per sync — decisions and action items. |
| `03_People/` | One note per person you work with — 1-on-1s and what you're waiting on. |
| `04_Templates/` | Blank starters for each kind of note. |
| `05_Weekly/` | Weekly summaries rolled up from the daily logs. |
| `06_Memory/` | Topic-scoped memories (`<topic>.md`) — facts, decisions, and gotchas you want Claude to recall later. |
| `Archive/` | Finished work, moved out of the active vault. |
| `current_tasks.md` | The "command center" at the vault root — the one file that tells you what's next. |
| `CLAUDE.md` | The conventions Claude follows in the vault. Yours to edit; your copy wins. |

Top-level `<PROJECT>.md` files (e.g. `PROJ-205-report-csv-refactor.md`) hold per-ticket or
per-topic working notes.

## The daily workflow

**Morning (pilot).** Open `current_tasks.md`, pick the top 1–3 tasks, and for anything complex
link out to a dedicated note (e.g. `[[PROJ-205-report-csv-refactor]]`) to keep the dashboard
clean.

**All day (sensor).** Keep today's daily log open and capture live: commands and outputs, error
codes and the fixes you tried, links, and "aha" moments. A new task surfaces mid-meeting? Drop a
`- [ ]` into the log immediately. Hit a problem you've seen before? Have Claude recall it from
your notes (see `notes-recall`) instead of working it out from scratch.

**After each chunk (log + reconcile).** Finished a meaningful piece of work? Log it and reconcile
`current_tasks.md` against it *before moving on* — tick what it closed, file what it genuinely
opened. Do this in the session that did the work: whether an item is done, and whether a loose end
is a real task or just something you noticed, is only reliably knowable while the context is still
live (see `update-daily-note`).

**Evening (prune).** Review the log, consolidate what's done, migrate unfinished `- [ ]` items to
`current_tasks.md`, and strip the noise so only the signal remains for later recall.

**End of week.** Roll the week's daily logs into a single summary in `05_Weekly/`.

## The skills

### `create-daily-note` — start your day
Creates today's note from the daily-log template with the dates filled in, creating the
`YYYY/MM_MonthName/` subdirectories if they don't exist yet. Won't overwrite an existing note.
**Triggers:** "start my day", "create today's log", "daily note", "new log entry".

### `update-daily-note` — log a session and reconcile the task file
Appends a terse summary of the current session to today's note, drawn from conversation context,
git activity, and errors hit. Populates **Work Stream** (raw technical log), **Done Today**
(`- [x]`), and suggested **Top Priorities**. Append-only for the log — never edits or removes
existing content; creates today's note first if it's missing.

It then **reconciles `current_tasks.md` against the same work**: ticks the items it closed
(rewriting each to say what happened, never striking through), edits the ones it advanced but
didn't finish, and files the loose ends that are genuinely new tasks — per the shared
[`references/task-placement-rules.md`](references/task-placement-rules.md). Loose ends no longer
pile up as `- [ ]` in **To Carry Forward**; that section gets a pointer line naming where they went.

The two halves are one skill because they answer the same two questions — *what did this finish?*
and *what's still open?* — and both answers need to know what actually happened. The evening prune
runs cold and can only read the text of a line. Run this after each meaningful chunk of work, not
only at day's end; the log half is append-only, so running it repeatedly just gives a more granular
Work Stream.
**Triggers:** "update my daily note", "log my session", "wrap up", "save my progress", "tick off
what we did", "I've finished X", "I'm done for now".

### `cleanup-daily-note` — evening prune
End-of-day tidy of a daily note: consolidates completed items into Done Today, migrates unfinished
`- [ ]` items into `current_tasks.md`, flags noise in Work Stream for your review *before* removing
anything, and checks off the Evening Prune list. Cleans today by default, or a past date when you
name one (backdated prunes also check whether an item was already resolved since that day).

Migration follows the shared **placement rules** in
[`references/task-placement-rules.md`](references/task-placement-rules.md) so `current_tasks.md`
doesn't drift — where an item goes (projects as headings, never dates; the origin date rides the
item as `` `(MM-DD)` ``), what may be admitted at all (~40 words; an action and a doer, so status
and reference facts don't become permanently-open checkboxes), and a **hard dedupe gate** that
requires reading the target section before writing. `update-daily-note` reads the same file, which
is what keeps two writers from governing the command center differently.

Because migration only ever adds, the pass also **prunes the sections it wrote to**: over-long
items are compressed (detail moves to the topic note, the item keeps a link) and non-tasks are
demoted to a section preamble or `06_Memory/`. Both are lossless, so they happen without asking.
Items that look overtaken by events are **proposed for deletion with the evidence** — verified
against the repo or git, never inferred — and removed only if you say so. Sections the pass didn't
write to are left alone; sweeping the whole file is a separate, user-initiated job.
**Triggers:** "cleanup my daily note", "evening cleanup", "prune my notes", "end of day cleanup",
"clean up the note for the 15th".

### `weekly-summary` — end-of-week rollup
Reads the most recent **completed** Mon–Sun daily logs, extracts meetings and completed work,
condenses them into a short note, and saves it to `05_Weekly/`. Always targets the last finished
week, never the one still in progress.

Also runs a **status check** over plan/bug/investigation notes and reports four buckets — stale
(non-terminal status gone quiet), items awaiting production verification, terminal-status files
ready to archive, and **in flight** (actively moving, so visibly *not* drift). It only reports;
it never moves or edits those files. A file carrying a `status:` but no `type:` is itself flagged,
since the vault's lifecycles key off `type` and an untyped file is invisible to type-based scans.

The condensation targets a note readable in ~2 minutes, so it is opinionated about **bullet length**
(~25–35 words, 40 as the ceiling), not just bullet count: raw measurements, derivation chains, and
process steps get pushed down into the linked note behind a `[[wikilink]]`, while reversed
conclusions and plan-killing findings are kept even when they cost words.
**Triggers:** "summarize the week", "weekly update", "what did we do this week", "it's Friday,
let's recap".

### `capture-meeting` — minute an impromptu call
Captures a call, huddle, or sync into `02_Meetings/YYYY-MM-DD-<topic-slug>.md` while recall is still
fresh, by interviewing you in small batches (2–3 questions at a time) for decisions, action items,
open questions, and context worth keeping — then stopping early if you've already covered it.
Decisions are recorded with their *reasoning* in the same bullet, since the outcome is usually
recoverable later but the rejected alternative never is. Also links the note into that day's daily
log (with the key outcome inline, not just a link) and creates or appends to each attendee's
`03_People/` note. Backdated capture is supported; a second call on the same subject the same day
appends a follow-up section rather than overwriting.

Action items you owe deliberately **stay** in the meeting note rather than being written straight to
`current_tasks.md` — they reach it through the normal `cleanup-daily-note` pass, which owns the
placement and dedupe rules, so only one skill ever writes that file.
**Triggers:** "capture the meeting", "log that call", "just got off a call", "quick sync with
&lt;names&gt;", "we just decided X on a call", "minute that". For a *solo* work session use
`update-daily-note` instead.

### `notes-recall` — recall project context
Looks up status, plans, decisions, and recent work by searching the vault **first**, before any
repo scan — the vault is small and authoritative for project context, while repo-wide scans are
slow and noisy. Searches the daily logs, `06_Memory/`, and project files; only falls back to the
repo after checking with you.
**Triggers:** "where are we with X", "what's the status of X", "let's continue work on X", "what
do my notes say about X".

### `notes-remember` — capture a memory
Saves a fact worth keeping beyond the session into a topic-scoped `06_Memory/<topic>.md` (keyed by
ticket, project, or feature), under a dated header. Pairs with `notes-recall`, which reads the same
files back.
**Triggers:** "remember that…", "save this", "note that…", "don't forget", "file this under X".

## Optional: local indexing

The vault is plain markdown, so you can also point a local tool at it — Obsidian's Smart
Connections, or a local model via Ollama — for offline semantic search. That's entirely optional;
the skills above are the primary interface.
