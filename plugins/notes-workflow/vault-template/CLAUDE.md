# notes/ vault — working conventions

The single source of truth for how any agent *uses* this `notes/` vault — when to reach for it
(recall and memory routing) and how to create, type, and maintain files in it. Per-type starter
templates (frontmatter + body skeleton) live in `04_Templates/` — copy the matching one when
creating a note.

> **This file is exempt from the frontmatter rule below.** `CLAUDE.md` is agent
> configuration — the file that *defines* the convention, not a content note subject to it —
> so it carries no typed frontmatter. It's the only such exception in the vault.

## This vault is authoritative for project context

For any recall/status/resume question about a project, ticket, or topic, search this vault
before any repo-wide search. Repo-wide scans (`grep -r`, `find .`, an Explore subagent on the
codebase) are slow and token-expensive, and the answer is usually already sitting here.

Where to look:
- Top-level `<PROJECT>.md` files (e.g. `PROJ-205-report-csv-refactor.md`) — per-ticket /
  per-topic working notes
- `current_tasks.md` — the command center
- `06_Memory/<topic>.md` — captured memories
- `01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` — daily logs

The `notes-recall` skill encodes this search ladder and triggers on most recall-shaped
phrasings. Even when it doesn't fire, prefer a cheap targeted search over a wide scan; if the
notes don't have it, say so and ask before pivoting to a repo scan.

## Memory routing: where a captured fact belongs

The always-loaded auto-memory (`~/.claude/.../memory/`) remembers the **collaborator**; this
vault's `06_Memory/` remembers the **work**. Before saving any fact: *would a brand-new session
on an unrelated task tomorrow still need it?*

- **Task-independent** — who the user is, how they want Claude to work, an always-relevant
  resource → **auto-memory** (types `user` / `feedback` / `reference`), kept tiny.
- **Task-scoped** — a ticket / service / feature fact, a bug, a decision, a gotcha, a
  `file:line` → **this vault's `06_Memory/<topic>.md`** via `notes-remember`.
- **Team-facing** → if your team keeps its own docs (a repo's `docs/`, a wiki), a fact your
  colleagues need belongs there, not here. This vault is yours.

Never put a work/project fact in the auto-memory — it belongs in `06_Memory/`. The auto-memory
may carry a one-line `reference` pointer to a `06_Memory/` topic, never a copy.

## Every new note gets typed frontmatter

Start every note with YAML frontmatter. Universal baseline (all notes):

```yaml
type: <one of the controlled values below>
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
```

## The document types

| type | for | extra fields | lifecycle |
|------|-----|--------------|-----------|
| `plan` | ticket plans, impl/feature/arch plans, specs, testing plans | `ticket` (opt), `status` | `planned → executing → merged → verifying-prod → done` |
| `investigation` | open-ended investigations, incidents, analyses (no ticket yet) | `ticket` (opt), `status`, `refs` (opt) | `investigating → root-caused → resolved → wontfix` |
| `bug` | tracked defects (HAS a ticket) | `ticket`, `status`, `refs` (opt) | `investigating → root-caused → fixing → merged → verifying-prod → resolved` (off-ramp `wontfix`) |
| `proposal` | feature/PoC proposals, idea docs | `status` | `draft → under-review → accepted → rejected → superseded` |
| `guide` | howtos, setup, tutorials, learning paths | `last_verified` | evergreen (no status) |
| `reference` | data references, vault README, convention docs | `last_verified`, `source` (opt) | evergreen (no status) |
| `presentation` | slide scripts, speaker notes | `audience` (opt) | none |
| `memory` | `06_Memory/` per-ticket fact notes | `ticket` (opt) | none |

## Structured-dir types

`log` (`01_Logs/` daily logs), `weekly-summary` (`05_Weekly/`), `meeting` (`02_Meetings/`),
`person` (`03_People/`). Use `meta` for singletons that fit no type (e.g. `current_tasks.md`).

## Bug vs. investigation

The discriminator is **the ticket**, expressed through the `type`:
- **`type: bug`** → a tracked defect. HAS a `ticket`. Carries the full diagnose-*and*-remediate lifecycle (see "Keep status current" below) — it ships code and follows the fix through to production.
- **`type: investigation`** → open-ended diagnosis with no ticket yet. Terminal at `root-caused`/`resolved`/`wontfix`; it does **not** ship code.

A bug is an investigation that has been **promoted**. Once you root-cause a defect, file a ticket, and decide to fix it, change `type: investigation` → `type: bug` and set the `ticket`. The diagnostic arc (`investigating → root-caused`) is shared between the two types, so `status` carries over unchanged across the promotion — you simply gain the remediation stages (`fixing → merged → verifying-prod → resolved`).

An investigation may carry `tags: [bug]` to flag "this is a defect" *before* a ticket exists — that marks a **candidate** bug, not a tracked one. An untracked defect is a gap: file the ticket (promoting it to `type: bug`) or flag it.

## Keep status current

When a session advances a doc's state (plan created, code merged, deployed, verified; or an
investigation root-caused/resolved), update its `status` + `updated` frontmatter, refresh the
matching `06_Memory/<ticket>.md` note, and add a line to today's daily log — proactively, as
part of wrapping up, without being asked.

Status is **forward-only**; bump `updated` on every transition. Lifecycle meanings:

**plan**
| status | meaning |
|--------|---------|
| `planned` | plan written, no code yet |
| `executing` | implementation in progress |
| `merged` | code merged to `develop` (or main), not yet deployed/verified |
| `verifying-prod` | deployed to staging; awaiting production verification |
| `done` | verified in production — work fully complete |

**bug** — the diagnostic arc of an investigation glued to the remediation arc of a plan, joined at `root-caused`:
| status | meaning |
|--------|---------|
| `investigating` | diagnosing; cause not yet pinned |
| `root-caused` | cause confirmed; decision point — fix, or off-ramp to `wontfix` |
| `fixing` | fix being written / on a branch, not yet merged (the plan-side `executing`) |
| `merged` | fix merged to `develop` (or main), not yet deployed/verified |
| `verifying-prod` | deployed to staging; awaiting production verification |
| `resolved` | verified fixed in production — terminal |

`wontfix` is the terminal off-ramp, reachable from `investigating`/`root-caused`.

**investigation:** `investigating → root-caused → resolved → wontfix`
**proposal:** `draft → under-review → accepted → rejected → superseded`

## Archival

A plan moves to `notes/Archive/` only when `status: done`; a bug or an investigation only when
`resolved`/`wontfix`. Plans and bugs stay at vault root through `verifying-prod` so they remain
visible while still in flight. Archival is **user-confirmed, never automatic** — never auto-move.

The weekly-summary skill scans plan/bug/investigation files and flags drift: a non-terminal
`status` with a stale `updated`, `verifying-prod` items to check, and terminal-state items ready
to archive.

## How items enter `current_tasks.md`

**One skill adds items here: `cleanup-daily-note`, the evening prune** — plus you, on direct
instruction. It applies the placement rules in the `notes-workflow` plugin's
`references/task-placement-rules.md` (PLACEMENT: rules 1–5 and the dedupe gate).

`update-daily-note` may **tick and update** items that already exist, but never adds one. New
tasks it opens during a session are staged in that day's `## ⏭ To Carry Forward` section, under
`###` headings naming the `current_tasks.md` heading they belong to, and the evening prune
migrates them. It applies the same reference's ADMISSION rules (6–7) when staging.

The split follows the two questions, not the two skills. *Is this a task at all?* needs the warm
context of the session that did the work, so it happens at Carry Forward. *Where does a new item
go in a file that grows all week?* — the heading match, the dedupe gate, the ordering — needs a
cold read of the whole file, so it happens once, in the evening, by one writer. Reconciling an
item that already exists needs neither, which is why ticking and updating stay warm.

**Never write here proactively by inference** — an ad-hoc edit bypasses those rules. This holds
even when your own work has just made a line here wrong: invoke `update-daily-note` to tick or
update it, stage a correction in Carry Forward, or say the line is stale and let the user decide.
The same applies in any repo; these conventions load wherever the vault is in play.

## How items leave `current_tasks.md`

A completed item is **not** struck through. Mark it `- [x]` and rewrite the text to say what
actually happened — the `cleanup-daily-note` skill sweeps `- [x]` items out of `current_tasks.md`
into that day's `## ✅ Done Today`, then deletes them from the command center. `- ~~struck~~`
without a checkbox reads as done to a human and as open to the sweep, so it never leaves; that is
how a section accumulates months of finished work.

Two consequences worth knowing:

- **Mark it done on the day it happened.** The sweep files items under the *current* daily log,
  so ticking a week-old completion backdates nothing and misfiles it. If the work is already
  recorded in an earlier day's Done Today, delete the item outright instead — it is duplication,
  not a pending migration.
- **Detail belongs in the daily log and the topic note, not here.** Verbosity is correct in
  `01_Logs/` (durable record) and in the per-topic working note (the reasoning); a
  `current_tasks.md` entry only has to carry enough to recognise the work and find it again.

A whole `# <Project>` section is deleted once every item under it is gone and its linked note has
reached a terminal `status`. Flagging a header `READY TO ARCHIVE` is a note to the next cleanup
run, not an archival in itself.

