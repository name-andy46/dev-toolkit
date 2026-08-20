---
name: create-daily-note
description: Creates a daily work log note in notes/01_Logs/YYYY/MM_MonthName/. Use this skill whenever the user wants to create a daily note, daily log, work log, start their day, or mentions anything about today's note or logging their work. Triggers on phrases like "daily note", "create today's log", "start my day", "work log", "daily log", "new log entry", or any request to create or open today's note.
---

# Daily Note Creator

Create today's daily work log note in `notes/01_Logs/YYYY/MM_MonthName/` using the vault's daily-log template.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Steps

1. Determine today's date.
2. Build the directory path: `notes/01_Logs/YYYY/MM_MonthName/` where `MM` is the zero-padded month number and `MonthName` is the full English month name (e.g., `notes/01_Logs/2026/03_March/`).
3. Build the filename: `YYYY-MM-DD.md` inside that directory (e.g., `notes/01_Logs/2026/03_March/2026-03-17.md`).
4. Check if the file already exists by running `ls notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md` via Bash. Do NOT use the Glob tool for this check — it may not find files in mounted/external directories. If the file exists (ls succeeds), tell the user the note already exists for today and stop — do not overwrite it.
5. Create the year and month directories if they don't already exist (e.g., `mkdir -p notes/01_Logs/2026/03_March/`).
6. Read the template from `notes/04_Templates/Daily Log Template.md`. The vault's copy is the only copy — the user can retune their daily-note layout and a plugin update will never overwrite it. If it's missing (a hand-made vault, or they deleted it), restore it from this plugin's own `vault-template/04_Templates/Daily Log Template.md` (`${CLAUDE_PLUGIN_ROOT}/vault-template/...`), mention that you did, and carry on.
7. Replace the two date placeholders in the template:
   - `{{date:YYYY-MM-DD}}` → ISO date, e.g., `2026-03-17`
   - `{{date:dddd, MMMM Do, YYYY}}` → full human-readable date, e.g., `Tuesday, March 17th, 2026`
8. Write the rendered template to the file path from step 3.
9. Confirm to the user that the note was created.

## Date formatting details

The long-form date uses this format: **Weekday, Month Dayth, Year**

For the ordinal day suffix:
- 1st, 21st, 31st
- 2nd, 22nd
- 3rd, 23rd
- Everything else gets "th" (4th, 5th, ... 11th, 12th, 13th, ... 20th, 24th, etc.)

Note: 11th, 12th, and 13th are exceptions — they use "th", not "st"/"nd"/"rd".

## Important

- The top-level `notes/01_Logs/` directory is expected to already exist in the vault. However, year and month subdirectories (e.g., `2026/03_March/`) should be created as needed.
- Never overwrite an existing note. If the file exists, just inform the user.
- Always use today's date. The user does not specify a date.
