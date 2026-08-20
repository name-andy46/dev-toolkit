---
name: notes-remember
description: Captures something the user wants remembered into a topic-scoped file under `notes/06_Memory/<topic>.md` in the markdown notes vault. Use whenever the user says "remember", "remember that", "remember about <project>", "save this", "save this for later", "note that", "keep in mind", "don't forget", "file this under X", "jot this down", or otherwise signals they want a fact retained beyond this session. Don't be shy — if the user is telling you a fact they clearly want preserved across sessions (a config value, a gotcha, a decision, a file:line reference), file it even if "remember" wasn't the literal word. Pairs with `notes-recall` (recall reads from the same `06_Memory/` plus the rest of the notes vault).
---

# notes-remember

Capture a memory into the user's markdown notes vault at `notes/06_Memory/<topic>.md`. The user treats the vault as Claude's primary persistent memory store.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Steps

1. **Identify the topic.** In order of preference:
   - Explicit reference in the user's message ("remember about PROJ-205 that…" → topic is `PROJ-205`).
   - Ticket key from the current branch (`git branch --show-current` — `feature/PROJ-210` → topic `PROJ-210`).
   - The file or module the conversation has been focused on (`widget_handler.py` → `widget-handler`).
   - If still ambiguous, ask once with a concrete proposal: *"Filing under `06_Memory/<your-guess>.md` — sound right, or pick a different topic?"* Don't ask twice.

2. **Slugify the topic** into a filename:
   - Ticket keys stay uppercase as-is: `PROJ-205` → `PROJ-205.md`.
   - Free-text: lowercase, hyphenate spaces/underscores, strip punctuation. `Monorepo restructure` → `monorepo-restructure.md`.

3. **Ensure the dir exists**: `mkdir -p notes/06_Memory` (idempotent).

4. **Check whether the file exists**: `ls notes/06_Memory/<slug>.md` via Bash. Don't use Glob — it can miss files in mounted directories.

5. **If the file does not exist**, create it with typed frontmatter followed by the H1. The
   vault convention (see `<vault>/CLAUDE.md`) requires `type: memory` frontmatter on every
   memory note:
   ```markdown
   ---
   type: memory
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   tags: []
   ---
   # <Human-readable topic>

   ```
   - `created` and `updated` are today's date in ISO form (`YYYY-MM-DD`).
   - If the topic is a ticket key, add a `ticket: <KEY>` line (e.g. `ticket: PROJ-205`); omit it for free-text topics.
   - E.g. header `# PROJ-205` or `# Monorepo Restructure`.

6. **Insert the memory** under a date header at the **top** of the file body (after the H1):
   - Today's date in ISO form: `YYYY-MM-DD`.
   - If `## YYYY-MM-DD` for today already exists, append the new bullet under it.
   - Otherwise insert a new `## YYYY-MM-DD` section directly after the H1, with the bullet under it.
   - Newest entries go at the top — this is rolling capture, not a chronological log, so latest context is the most useful when the user opens the file later.
   - **Bump `updated:`** in the frontmatter to today's date on every write to an existing file.
   - **Legacy file with no frontmatter:** if an existing file starts straight at `#` with no `---` block (created before this convention), add the `type: memory` frontmatter while you're in there — set `created` to the oldest `## YYYY-MM-DD` already in the file and `updated` to today.

7. **Confirm** to the user with the file path and a one-line preview. E.g., *"Saved to `notes/06_Memory/PROJ-205.md` — 'report csv refactor uses streaming chunks, 10k row default'."* Keep it short; the user is mid-flow.

## File format

```markdown
---
type: memory
ticket: PROJ-205
created: 2026-05-18
updated: 2026-05-20
tags: []
---
# PROJ-205

## 2026-05-20
- report csv refactor uses streaming chunks, default chunksize 10000
- null-as-fresh fix at handlers/widget_handler.py:147

## 2026-05-18
- lookup must drop the revision filter — query by ID only
```

One bullet per memory. Terse — think commit messages, not prose. Include file paths, line numbers, commit SHAs, PR/issue refs, exact commands when relevant. Those details are why the user is asking you to remember it — preserve them verbatim, don't paraphrase.

## What counts as a memory worth capturing

The trigger word doesn't have to be literally "remember." Capture into `06_Memory/` when the user signals durable intent: *"save this for later"*, *"note that"*, *"keep in mind"*, *"don't forget"*, *"file this under X"*, *"jot this down"*. Also reasonable to capture when the user volunteers a hard-won fact in a way that clearly expects it to stick (an exact config value with a "btw" preamble, a gotcha they want recorded). When in doubt and the cost of asking is low, ask: *"Want me to file that under `06_Memory/<topic>.md`?"*

If the user is just narrating the present session ("I'm going to refactor the handler now"), that's not a memory — leave it alone, or suggest `/update-daily-note` if they're trying to log session work.

## Edge cases

- **Vault not found**: work the ladder in [`references/vault-resolution.md`](../../references/vault-resolution.md) all the way to the end — including the offer to create a vault. Only stop if the user declines; never write notes outside a vault.
- **Topic better suits a daily log**: if the user says "remember today I shipped X", that's daily-log territory — point them at `/update-daily-note` but offer to file it in `06_Memory/` if they want durable capture instead.
- **Two plausible topics**: pick the more specific one (a ticket key beats a generic module name) and mention your choice in the confirmation so the user can redirect if it's wrong.

## Related

`notes-recall` reads from the same `06_Memory/` files plus the rest of the notes vault when the user asks to resume work, check status, or look something up.

