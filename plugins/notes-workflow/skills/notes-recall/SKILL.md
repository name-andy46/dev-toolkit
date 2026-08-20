---
name: notes-recall
description: >-
  Looks up project context (status, plans, recent work, decisions) by searching the user's markdown notes vault at `notes/` BEFORE scanning the repo. Use whenever the user says "let's continue work on X", "let's continue with X", "let's start with X", "let's pick up where we left off", "where are we with X", "where did we leave off on X", "what's the status of X", "what was the last action on X", "what do my notes say about X", "find X in my notes", or any other phrasing that signals they want to resume or recall context on a project, ticket, service, or topic. CRITICAL: do not launch `grep -r` across the repo, `find` from the workspace root, or an Explore subagent on the codebase as your first move — a repo-wide scan is slow and expensive when the answer is already sitting in the notes vault. Search the notes vault first; only fall back to the repo after asking the user. Use this skill aggressively even when the user doesn't explicitly mention notes.
---

# notes-recall

Look up project context from the user's markdown notes vault (located per *Where the vault lives* below). The vault is the user's authoritative store for project plans, status, decisions, and historical context. **Search it first. Then stop.**

## The cardinal rule

The repo is large and noisy; the notes vault is small and authoritative for project context. A repo-wide scan costs time and tokens to rediscover something the notes already record.

So: **no repo-wide Grep, no `find .` from the workspace root, no Explore subagent on the codebase as your first move.** Search the notes vault. If after going through the search ladder below you genuinely have nothing useful, say so out loud and ask before pivoting to a repo scan: *"Nothing in your notes about <X> — want me to grep the repo, or do you remember a different name for it?"* The user often remembers the exact file/topic name they used and that's faster than a scan.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Vault layout

```
notes/
├── 01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md   # daily logs
├── 02_Meetings/                              # one note per sync
├── 03_People/                                # one note per teammate
├── 04_Templates/                             # note templates
├── 05_Weekly/                                # weekly summaries
├── 06_Memory/                                # memories captured by `notes-remember`
├── current_tasks.md                          # the user's "command center"
├── <PROJECT>.md                              # top-level project files (e.g. PROJ-205-report-csv-refactor.md)
└── <subdir>/                                 # ad-hoc topic dirs (e.g. product-research/)
```

## Identify the subject

Pull the subject from the user's message — usually a ticket key, project name, service name, or feature name. Keep two forms:
- **Slug** for filename matching: ticket keys uppercase as-is (`PROJ-205`); free-text lowercase hyphen-separated (`monorepo restructure` → `monorepo-restructure`).
- **Original phrasing** for content greps (case-insensitive).

## Search ladder

Run these in order. **Stop as soon as you have enough to answer the user's question** — you don't need to exhaust every step.

Use the **Glob**, **Grep**, and **Read** tools throughout — not shell commands. They behave
identically on Windows, macOS, and Linux, whereas `ls`, `grep`, `seq`, and `date -d` don't exist
or don't take the same flags in PowerShell. If one of those tools isn't available in the
environment you're running in, fall back to the shell — POSIX commands on Linux/macOS, the
PowerShell equivalents on Windows — keeping the same scoping discipline each step describes.

1. **Memory file (exact filename match)** — read `notes/06_Memory/<slug>.md`. If it reads back, that's usually the answer; the newest date header at the top is what the user wants.

2. **Top-level project files** — Glob `*.md` at the vault root and look for filenames containing the subject as a substring, case-insensitive. Project notes live at the root, like `PROJ-205-report-csv-refactor.md` or `monorepo-restructure-plan.md`. Read the matches.

3. **`current_tasks.md`** — Grep for the subject, case-insensitive, scoped to `notes/current_tasks.md`. The command center; active projects usually have a section here.

4. **Recent daily logs (last ~14 days only)** — don't scan every log ever written. Work out the last 14 calendar dates yourself (you know today's date — no shell date arithmetic needed), then run **one** Grep: the subject as the pattern, case-insensitive, path `notes/01_Logs`, glob `**/*.md`, output mode `files_with_matches`. Keep the hits whose `YYYY-MM-DD.md` filename falls inside that window and read those.

5. **Subdirectories** — Glob the vault root for ad-hoc directories (e.g. `product-research/`), then a Grep scoped to the one that matches. Scoping is what keeps this cheap; subdirs are bounded.

6. **Fallback** — if all of the above turn up nothing, **tell the user and ask before scanning the repo or running anything wider**. Do not silently pivot.

## Presenting what you found

Synthesize, don't dump. The user asked "where are we with X" — give them the answer, not a file paste.

Format like:

> **PROJ-205 — report csv refactor**
> Last touched: 2026-05-18 (daily log mentions PR #120 merged for test infra)
> Plan: `notes/PROJ-205-report-csv-refactor.md` — switching to streaming chunks, default 10k rows
> Open items (from `current_tasks.md`): re-test the export endpoint after the storage migration

Cite file paths so the user can jump to them in their editor. Use `file_path:line_number` form when pointing at a specific line.

If you find stale or conflicting info across multiple files (one says "in progress", another says "done"), surface the conflict — don't pick a side silently.

## Costs and budget

Reading the vault should be cheap: one or two targeted Glob/Grep calls and 1–3 Read calls on the files they point at. If you find yourself spawning an Explore subagent, Grepping the whole vault unscoped, or reading a dozen daily logs, stop — you're probably searching wrong. Re-check the ladder.

Repo-wide scanning is expensive and slow. Treat it as the last resort, not the first move.

## Edge cases

- **No match on the slug, but partial matches in filenames**: present the top 2–3 candidate paths and let the user pick rather than guessing.
- **Vault not found**: work the ladder in [`references/vault-resolution.md`](../../references/vault-resolution.md) all the way to the end — including the offer to create a vault. Only stop if the user declines; never write notes outside a vault.
- **Subject is genuinely ambiguous**: ask one short clarifying question — e.g., *"`PROJ-205` shows up in both `06_Memory/PROJ-205.md` and `PROJ-205-report-csv-refactor.md`. Pull from both, or just one?"*

## Related

`notes-remember` writes new memories into `06_Memory/<topic>.md`, which this skill reads in step 1 of the search ladder.

