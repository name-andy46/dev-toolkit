---
type: guide
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_verified: YYYY-MM-DD
tags:
  - vault
---
# Start here

This folder is your notes vault. It's plain markdown files — nothing proprietary, nothing to log
into. You can read and edit any of it in any text editor. [Obsidian](https://obsidian.md) makes it
nicer (it follows the `[[links]]` between notes), but it's entirely optional.

You don't have to learn this layout. Ask Claude in plain English — *"create today's note"*,
*"what did I work on last week?"*, *"remember that the deploy needs the VPN"* — and it files
things in the right place. This page is here for when you want to look around yourself.

## What's in here

| Folder | What lands in it |
| --- | --- |
| `01_Logs/` | One note per working day, filed by year and month. Your diary. |
| `02_Meetings/` | One note per meeting or call — who was there, what was decided, who owes what. |
| `03_People/` | One note per person you work with; what you've discussed, what they owe you. |
| `04_Templates/` | Blank starters for each kind of note. Copy one when writing by hand. |
| `05_Weekly/` | End-of-week summaries, rolled up from that week's daily logs. |
| `06_Memory/` | Facts worth keeping past today, one file per topic. |
| `Archive/` | Finished work, moved out of the way. Nothing is ever archived without asking you. |
| `current_tasks.md` | Everything still open, grouped by project. The to-do list. |
| `CLAUDE.md` | The conventions Claude follows in here. Editable — your copy wins. |

## The daily rhythm

Most people use three of the skills and ignore the rest:

- **Morning** — *"create today's note"* starts the day's log from the template.
- **During the day** — *"log my session"* or *"I've finished X"* appends what happened and ticks
  off the matching task.
- **End of day** — *"evening cleanup"* moves unfinished work to `current_tasks.md`, files what got
  done, and prunes the noise.

Then *"summarize the week"* on a Friday, and *"remember that…"* / *"what do my notes say about…"*
whenever something is worth keeping or looking up.

## A couple of things worth knowing

The templates in `04_Templates/` contain `{{date:YYYY-MM-DD}}` placeholders. Those expand
automatically if you have Obsidian's Templates plugin turned on; the skills fill them in
themselves, so this only matters if you're creating a note by hand.

Nothing here is deleted or archived without asking you first. If a skill wants to move or prune
something, it proposes and waits.
