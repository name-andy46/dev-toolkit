---
name: capture-meeting
description: >-
  Captures an impromptu meeting, call, huddle, or sync into a structured note in the notes vault's `02_Meetings/` — interviewing the user for attendees, decisions, action items, and open questions while the call is still fresh, then linking it into today's daily log and each attendee's `03_People/` note. Use this whenever the user has just finished talking to people and wants the outcome recorded: triggers on "capture the meeting", "log that call", "we just decided X on a call", "quick sync with <names>", "just got off a call", "minute that", "record what we agreed", "note down this discussion", or any mention of a huddle/standup/catch-up whose decisions would otherwise be lost. Reach for it even when the user doesn't say "meeting" — if they're describing something a group of people just agreed, that's this skill. For a solo work session use `update-daily-note` instead; this one is specifically for what happened between people.
---

# Capture Meeting

Impromptu calls are where a surprising share of real decisions get made, and they are
the least likely to be written down. The decision lives in two or three people's heads,
each remembering it slightly differently, until someone asks three weeks later why the
repack window is 11:00 UTC and nobody can reconstruct the reasoning.

This skill exists to close that gap in the two minutes after a call ends, while recall
is still perfect. Speed is the whole point — a capture process that feels like paperwork
will not survive contact with a busy week.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

Consult the vault's own `CLAUDE.md` for frontmatter conventions — it is authoritative.
This skill implements the already-declared `meeting` (`02_Meetings/`) and `person`
(`03_People/`) types.

## The interview

Ask in **small batches, not one long questionnaire.** The user just got off a call and
is holding the content in short-term memory; a wall of questions invites a shrug and a
one-line answer. Two or three questions at a time, and let their answers steer what you
ask next.

Open with the two that unlock everything else:

> Who was on the call, and what was it about?

From their answer you usually get the topic, the attendees, and enough context to ask
sharper follow-ups. Then work through the four things that matter, adapting the wording
to what they've already told you:

1. **Decisions** — what was actually settled? Push gently for the *why*, because that's
   the part that decays fastest and is worth the most later. "We're going with 11:00 UTC"
   is worth half as much as "11:00 UTC because it's the write trough and clear of the
   nightly export at 10:36."
2. **Action items** — who owes what, and by when? Distinguish what *the user* owes from
   what *someone else* owes them; those get filed differently below.
3. **Open questions** — what got raised and deliberately left unresolved? These are
   easy to forget precisely because nothing was decided, and they're often the seed of
   the next call.
4. **Context worth keeping** — numbers quoted, constraints named, someone's strong
   opinion, a system or ticket referenced. Only if there is any; don't manufacture it.

**Stop asking when the user is done talking.** If they answer the first question with a
complete braindump covering all four, don't march through the remaining prompts for the
sake of it — write the note and ask only about genuine gaps. The interview is a
scaffold for recall, not a form to complete.

If the user invoked the skill *with* content already (`/capture-meeting quick call with
Priya, we settled the repack window`), treat that as the answer to question one and
continue from there rather than asking what they just told you.

### Things worth asking about that users routinely omit

- **The date**, if the call wasn't today. Backdated capture is normal — someone
  remembers on Thursday that Tuesday's call was never written up.
- **Whether a decision reverses an earlier one.** These are gold, and they're usually
  mentioned in passing ("yeah we're not doing the thing we said last week"). Ask what it
  supersedes so the note can say so explicitly.
- **Full names**, when the user gives first names only and there's ambiguity. You need
  a stable name to key the `03_People/` note on.
- **Whether anything was decided that they disagree with.** Not to litigate it, but
  because a recorded dissent is enormously useful three months on. Ask lightly and drop
  it if they don't bite.

## Writing the meeting note

**Path:** `notes/02_Meetings/YYYY-MM-DD-<short-slug>.md`
**Template:** `04_Templates/Meeting Template.md` — the structure below matches it.

The slug is 2–4 words naming the *topic*, not the ceremony — `2026-08-03-repack-window.md`
beats `2026-08-03-quick-sync.md`. A month later the topic is what you'll search for.
If a note already exists at that path, this is a second call on the same subject the
same day: append a `## Follow-up (HH:MM)` section rather than overwriting.

```markdown
---
type: meeting
date: YYYY-MM-DD
attendees: [Name One, Name Two]
tags: []
---
# <Topic> — <Day>, <Month DD, YYYY>

**Attendees:** [[Name One]], [[Name Two]]
**Context:** <one line on why this call happened — the trigger, not the agenda>

## Decisions
- **<What was decided>** — <why, in the same breath. Include the number, constraint,
  or trade-off that drove it.>

## Action Items
- [ ] <me> — <what I owe> `(due: YYYY-MM-DD)`
- [ ] <Name> — <what they owe> #waiting-on

## Open Questions
- <what was raised and left unresolved, and who would need to answer it>

## Notes
- <context worth keeping: figures quoted, constraints named, systems referenced>
```

Omit any section that would be empty. A meeting note with three decisions and no open
questions should not carry an empty **Open Questions** heading — blank scaffolding
trains the eye to skip sections, which is exactly wrong for a document whose value is
that someone reads it later.

**Link outward liberally.** Wikilink attendees, tickets (`[[PROJ-205]]`), services, and
any vault note the discussion touched. These links are how the meeting resurfaces when
someone is reading about the topic six weeks later and has no idea a call ever happened.

### On writing decisions

The failure mode is recording the *outcome* and losing the *reasoning*. Someone reading
this later can usually see what was decided by looking at the system; what they cannot
recover is why the alternatives were rejected.

When the user mentions an alternative that was considered and dropped, keep it — one
clause is enough: "Chose `pg_repack` over `VACUUM FULL` — the latter takes ACCESS
EXCLUSIVE on a hot-path table."

If a decision was made on incomplete information, say so. "Going with X for now,
revisit if the audit shows more than 30 orgs" is a far more useful record than "Decided:
X", because it tells a future reader the decision has a trigger for reopening.

## After the note: two updates

Both of these are what make the meeting note *findable* rather than a file that exists.
Do them as part of the capture, not as a follow-up question.

### 1. Today's daily log

Append one line under `## 🤝 Meetings & Syncs` in
`notes/01_Logs/YYYY/MM_MonthName/YYYY-MM-DD.md`, using the meeting's date, not today's,
when they differ:

```markdown
- **<Topic>** with <names> → [[YYYY-MM-DD-<slug>]] — <the single most important outcome>
```

That trailing clause matters. A bare link makes the reader open a file to find out
whether it's relevant; the outcome inline usually answers their question outright.

If the daily note doesn't exist yet, create it from `04_Templates/Daily Log Template.md`
rather than writing a bare file — the template carries the section structure the rest of
the notes tooling depends on.

Action items the user owes are deliberately **not** written to `current_tasks.md` here.
They live in the meeting note and reach the task file through the normal
`cleanup-daily-note` pass — the only skill that adds to it, and the one that owns the
placement and dedupe rules. Several writers appending to that file through the day, each
seeing a different snapshot of it, is how it drifts.

### 2. Attendee notes in `03_People/`

For each attendee other than the user, create or update `notes/03_People/<Name>.md`.
This directory starts empty for most vaults, so you will often be creating the first
note for a person — that's expected, not a signal you've got the path wrong.

Follow `04_Templates/People Template.md`:

```markdown
---
type: person
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
---
# <Name>
**Role:** <if known — otherwise omit the line rather than writing "Unknown">
**Services:** [[<service>]]

## ⏳ Pending Tasks
- [ ] #waiting-on <what they owe> (from [[YYYY-MM-DD-<slug>]], YYYY-MM-DD)

## 📝 Recent Syncs
- YYYY-MM-DD: <one line> → [[YYYY-MM-DD-<slug>]]
```

For an existing person note, **append** to Recent Syncs and Pending Tasks; don't rewrite
the file. Bump `updated`. If the meeting resolved something they owed, check off that
`#waiting-on` item rather than leaving a stale one — a Pending Tasks list nobody prunes
stops being read.

Only capture a role or service affiliation if the user actually said it. An invented
"Role: Backend Engineer" is worse than no line, because it looks authoritative.

## Confirm, briefly

Report what you wrote — the meeting note path, the daily-log line, and which person
notes were created versus updated. Note the created/updated split explicitly; the first
note for someone is worth knowing about.

Then surface anything you were unsure of, in one or two lines: a name you couldn't
resolve to a full name, an action item with no clear owner, a decision you recorded
without its reasoning because the user didn't offer one. These are cheap to fix in the
moment and expensive to fix in a month.

Keep the confirmation short. The user just spent two minutes on this and wants to get
back to work.

