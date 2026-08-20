# Locating (or creating) the notes vault

Every skill in this plugin reads and writes a single markdown **vault**. This file is the one
place that says how to find it, so the rule can't drift between eight skills.

## The ladder

Try these in order and stop at the first hit:

1. **`$NOTES_PATH`** — an absolute path, set by the user. Highest precedence, always wins.
2. **A `notes/` directory under the current working directory.** Covers repos and containers that
   keep the vault alongside the code.
3. **`~/notes`** — the default location for a vault this plugin created.
4. **Nothing found → offer to create one** (below). Do not stop with an error; a first-time user
   has no vault yet, and that's the normal case, not a failure.

## What counts as a vault

A directory is a vault only if it contains a `CLAUDE.md` at its root. That file holds the
conventions every skill depends on — the document types, the frontmatter, the status lifecycles —
so a directory without it is not a vault this plugin can operate on.

This matters on rung 3. If `~/notes` exists but has no `CLAUDE.md`, do **not** adopt it: it's some
other directory that happens to share the name. Treat it as "not found" and ask the user where
their vault is, or whether to set one up somewhere else.

## Creating a vault (rung 4)

**Always ask first.** Never create a vault as a side effect of another request.

> I don't see a notes vault. Shall I create one at `~/notes`? (Or tell me where you'd like it —
> for example inside a Dropbox or iCloud folder if you want it synced.)

On yes:

1. Copy this plugin's entire `vault-template/` directory to the chosen location. Copy it
   wholesale — don't hand-create directories from a list, or the vault will drift from what the
   plugin actually ships.
2. Replace the `YYYY-MM-DD` placeholders in the new vault's `START_HERE.md` frontmatter with
   today's date.
3. Tell the user, in one or two lines, where it is and point them at `START_HERE.md` for the tour.
4. If the location isn't one the ladder will find next time (anything other than `~/notes`, or a
   `notes/` directory in the working directory), tell them to set `NOTES_PATH` so it's found
   automatically, and show the exact line for their shell profile:

   ```bash
   export NOTES_PATH="/the/path/they/chose"
   ```

5. Then carry on with whatever they originally asked for. Creating the vault is a step on the way,
   not the end of the task.

If they say no, don't write notes anywhere else. Say what you'd have done and stop — a note
written outside the vault is a note that's lost.

## Rules that apply once it's resolved

- Everything is relative to the vault root. Where a skill's instructions say `notes/`, that means
  the resolved vault, whatever its real path.
- **Never write vault files anywhere else.** Not the working directory, not a temp dir. If the
  vault can't be resolved and the user declined to create one, stop.
- Read the vault's own `CLAUDE.md` before creating or editing a note in it. The user may have
  tuned the conventions, and their copy wins over anything assumed here.
- Prefer `ls` via Bash over the Glob tool when checking whether a vault file exists — Glob can
  miss files in mounted or symlinked directories.
