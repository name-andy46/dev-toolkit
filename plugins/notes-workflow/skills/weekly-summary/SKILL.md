---
name: weekly-summary
description: Generates a condensed weekly summary note from the previous Mon–Sun daily logs. Use this skill whenever the user wants to summarize the week, create a weekly update, generate a weekly note, wrap up the week, or review what happened this week. Triggers on phrases like "summarize the week", "weekly summary", "weekly update", "weekly note", "what did we do this week", "create a weekly recap", or any request to roll up the week's work into a summary. Also trigger when the user says something like "it's Friday, let's recap" or "end of week roundup".
---

# Weekly Summary Generator

Read the Mon–Sun daily logs for the most recent completed work week, extract meetings and completed work, condense it into a short weekly note, and save it to `notes/05_Weekly/`.

The note serves two readers at once: the author, who needs the week's detail and its loose ends, and a **manager or CTO with 20 seconds and no context**, who needs `## The Short Version` at the top (Step 5) and nothing else.

## Where the vault lives

Paths below are relative to the notes vault. **Resolve the vault as described in
[`references/vault-resolution.md`](../../references/vault-resolution.md)** — `$NOTES_PATH`, else a
`notes/` directory under the working directory, else `~/notes`, else offer to create one. Where a
path below says `notes/`, that's the vault root.

## Step 1: Determine the week range

- Today is available via the system date.
- The **target week** is always the most recent completed Mon–Sun period — i.e., the last full week that has already ended.
  - Find the most recent Sunday before today, then go back to the Monday of that same week.
  - Example: if today is Monday Mar 23, the target week is Mon Mar 16 – Sun Mar 22.
  - Example: if today is Wednesday Mar 25, the target week is still Mon Mar 16 – Sun Mar 22 (the last completed week).
  - Never include today or any day in the current (still-in-progress) week.
- Compute `week_start` (Monday) and `week_end` (Sunday) as ISO dates.

## Step 2: Collect daily note paths

For each calendar day from `week_start` to `week_end`:
1. Build the path: `notes/01_Logs/YYYY/NN_MonthName/YYYY-MM-DD.md`
   - `NN` = zero-padded month number (e.g., `03`)
   - `MonthName` = full English month name (e.g., `March`)
2. Check if the file exists — if not, skip it silently.
3. Read the file.

## Step 3: Scan plan / bug / investigation files for status drift

Independently of the daily logs, scan the lifecycle-tracked **work files** at the vault root for
status drift. See `notes/CLAUDE.md` (the document-type table + "Keep status current") for the
authoritative lifecycles.

1. List `notes/*.md` and read the YAML frontmatter of each. Consider only files that HAVE a
   `status:` field — that's the three tracked types: `plan`, `bug`, `investigation`. Ignore
   reference docs, guides, proposals, and presentations.
2. **Terminal states differ by type** — use the right one when bucketing:
   - `plan` → terminal is `done`; in-flight verification is `verifying-prod`.
   - `bug` → terminal is `resolved` (or `wontfix`); in-flight verification is `verifying-prod`.
   - `investigation` → terminal is `resolved` (or `wontfix`); no `verifying-prod` stage.
3. Bucket each file:
   - **Drifting** — `status` is NOT a terminal state (per its type above) AND `updated` is older
     than ~10 days before `week_end`. These may be stale / forgotten.
   - **Awaiting production verification** — `status: verifying-prod` (plans and bugs). Surface so they
     get checked.
   - **Ready to archive** — `status` IS a terminal state (`done` for plans; `resolved`/`wontfix`
     for bugs and investigations) but the file is still at vault root (not yet in `notes/Archive/`).
   - **In flight** — `status` is non-terminal AND `updated` is recent (within ~10 days of
     `week_end`), OR the file was touched during the target week. This is work that is actively
     moving, or deliberately parked awaiting a decision. Report it so it is visibly *not* drift —
     without this bucket, healthy active work is either invisible or misread as stale.
4. **A file missing its `type:` field is itself a finding.** The vault's lifecycle conventions key
   off `type`, so an untyped file is invisible to type-based scans. If a file has a `status:` but
   no `type:`, still bucket it (infer the type from its `status` values and content) and flag the
   missing field inline so it can be fixed.
5. Carry these buckets into the output (Step 6 below). Do not modify or move any file here — this
   step only reports.

## Step 4: Extract sections

From each daily note, extract the content of three sections:
- `## 🛠 Work Stream (The "Sensor")` — read for context only
- `## 🤝 Meetings & Syncs`
- `## ✅ Done Today`

A section ends when the next `##` heading begins.

**Skip a day entirely if both Meetings and Done Today are empty** — "empty" means the section contains only blank lines, bare `-` bullets, or `- [ ]` / `- [x]` with no description text.

The Work Stream is background context: use it to understand the reasoning, root causes, and technical detail behind the Done Today items. Do not copy it directly into the summary — but do use it to write richer, more specific bullets (e.g., if Done Today says "fixed schema bug" and Work Stream explains it was `fields.Int` → `fields.Str` in `schema.py:126`, the summary bullet can include that specificity).

## Step 5: Synthesize a condensed summary

Write the weekly note body. The goal is brevity: someone should be able to read the entire note in under 2 minutes.

### Meetings section

List meetings grouped by day. For each day that had real meetings:
- One line per meeting: `- **Day Mon DD**: <concise description>`
- Include who was involved and what was decided/clarified, if present in the notes.
- Omit days with no meetings.

### Done This Week section

Condense the "Done Today" lists across all days into a tight grouped list:
- Merge related items (e.g., "Created server-start skill", "Created server-stop skill", "Created server-status skill" → "Created 3 Flask server lifecycle skills (start, stop, status)")
- Keep items that represent distinct outcomes or decisions — not process steps.
- Drop items that are purely administrative noise (e.g., "updated placeholder", "fixed typo").
- Aim for 5–10 bullets total, fewer if the week was light.

### Keep bullets short — this is where the note gets bloated

Bullet **count** is not the binding constraint; bullet **length** is. Ten disciplined bullets read
in well under a minute, while ten sprawling ones blow the 2-minute budget on their own. A section
that satisfies "5–10 bullets" can still be 700 words and fail the actual goal.

**Target ~25–35 words per bullet; treat 40 as the ceiling.** If a bullet runs longer, it is
carrying detail that belongs in the linked note.

The single most useful test: **would this sentence prove the conclusion, or is it the conclusion?**
Evidence proves; summaries state. Keep the conclusion, link to the evidence.

Push down into the linked note, never into the weekly:
- **Raw measurements and counts** — signal values, row counts, per-org tallies, before/after metric
  series. Keep the one headline number that makes the outcome legible; drop the supporting set.
- **Derivation chains** — the reasoning that produced a verdict. Keep the verdict and the number
  that decides it.
- **Process steps** — "ran it across dev and prod", "spun out a note", "reviewed the code". These
  answer *what steps did I take*, not *what changed*.

Keep, even when it costs words:
- **Corrected premises and reversed conclusions** — the outcome, not the whole story of the reversal.
- **Findings that killed a plan or changed a decision** — the most valuable line in most weeks.
- **Durable method rules** — lessons that generalize past this week's task. Compress hard: one line
  each, grouped into a single trailing block rather than given their own bullets.

**Add a wikilink to the spun-out note** (`[[note-name]]`) whenever detail is pushed down, so the
full record is one click away instead of duplicated. A bullet that links is allowed to be shorter
than one that does not.

Grouping many bullets under a small number of bold thematic sub-headers is encouraged — it makes
the week's shape legible at a glance. If one group grows past ~4 bullets and is doing two different
jobs, split it (e.g. "Bugs closed in production" vs "Tickets filed") rather than letting it sprawl.

**Before writing the file, check yourself:** count the bullets and skim for any that exceed ~40
words. Rewriting an over-long bullet at draft time costs far less than the reader's attention.

### The Short Version — write it last, place it first

Every weekly note opens with a `## The Short Version` section written for a **manager or CTO who
has about 20 seconds and no context whatsoever**. It is not a teaser for the detail below — it is
the only part many readers will ever read, so it has to stand on its own.

Write it **after** the rest of the note exists. It is a compression of `Done This Week`, and you
cannot compress what you have not yet written. Then place it directly under the `#` title, above
`## Meetings` / `## Done This Week`.

**Rules:**

- **Six bullets maximum, ~80 words for the whole section.** That is the 20-second budget. Fewer is
  better. One line per bullet: a bold clause naming the outcome, then plain English explaining it.
- **No exact numbers anywhere in this section.** No counts, measurements, durations, percentages,
  money, or versions — not even small ones like "two security holes". Figures invite scrutiny the
  reader has no time for, and every one of them already appears in the detail sections below. Write
  "functions were failing", not "18 functions"; "now none", not "~32 per run → 0".
- **No internal vocabulary at all.** No ticket ids, PR numbers, commit hashes, file paths, function
  or variable names, tool or library names, log-line names, ADR numbers, spec or change names, repo
  jargon, or runtime versions. If a term would make the reader ask "what is that?", it is banned.
- **Order by what the reader might have to act on**, never chronologically:
  1. **Unfixed risk** — anything security-, data- or customer-affecting that is still open. Mark `⚠️`.
  2. **Blocked, or finished but not yet live** — and what it is waiting on.
  3. **Shipped work**, most consequential first.
- **Every bullet must close.** Say what was wrong or built *and* where it now stands — "live in all
  environments", "not yet in production", "not fixed yet". A bullet that leaves the reader hanging
  has failed, however accurate it is.

**The test — apply it to every bullet before writing the file.** Read the bullet as someone who has
never seen this codebase, and list the questions it raises. *Why that runtime version? What is a
REPORT line? What does that acronym mean? Where was that recorded? Why does any of this matter?*
If a single question survives, the bullet is still written for you rather than for them. Rewrite it
in the words you would use out loud to a non-engineer.

**Worked example**, same week, before and after:

> ❌ On python3.13 a serverless function timing out or running out of memory writes nothing but a
> `REPORT` line, so 3 of 11 error terms matched nothing and 18 production functions raised zero
> alerts; ADR-0029 recorded.

> ✅ **Fixed silent production crashes** — we were not catching timeout and out-of-memory errors.
> Functions were failing with no alert to anyone. Live in all environments.

The detail in the ❌ version is not deleted from the note — it stays in `Done This Week`, where a
reader who wants it will find it. The Short Version is the door, not the room.

## Step 6: Write the output file

**Filename format:**
- Same month: `W{nn}_{MmmDD-DD}.md` (e.g., `W12_Mar16-22.md`)
- Spanning months: `W{nn}_{MmmDD-MmmDD}.md` (e.g., `W14_Mar31-Apr6.md`)
- `{nn}` is the ISO week number, zero-padded to 2 digits (e.g., `W01`, `W12`)
- Month abbreviations are 3-letter English (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec)
- Day numbers have no zero-padding (e.g., `W12_Mar3-9.md`, not `W12_Mar03-09.md`)
- No spaces anywhere in the filename

**Computing the ISO week number:** ISO week 1 is the week containing the first Thursday of the year. Weeks start on Monday.

**File path:** `notes/05_Weekly/<filename>`

**File content:**

```markdown
---
type: weekly-summary
week_start: YYYY-MM-DD
week_end: YYYY-MM-DD
---
# Week of <Mon Abbr DD> – <Sun Abbr DD>, YYYY

## The Short Version
- **<outcome in plain English>** — <where it now stands. No figures, no jargon.>
... (max 6 bullets, ~80 words total)

## Meetings
- **<Day Abbr DD>**: <meeting summary>
...

## Done This Week
- <condensed bullet>
...

## Status Check
**Drifting (no update in 10+ days, not in a terminal state):**
- `<file>.md` — type: <plan|bug|investigation>, status: <status>, updated <date>

**Awaiting production verification:**
- `<file>.md` — type: <plan|bug>, updated <date>

**Ready to archive (terminal status, still at root):**
- `<file>.md` — status: <done|resolved|wontfix>, move to notes/Archive/ once confirmed

**In flight (no action needed):**
- `<file>.md` — type: <plan|bug|investigation>, status: <status>, updated <date> — <one clause on why it is active, e.g. "PR raised 07-27" or "awaiting go-ahead by choice, not drift">
```

If there were no meetings at all that week, omit the Meetings section entirely.

**`The Short Version` is never omitted** — if the week was light, it gets two bullets, not zero.

Omit any empty bucket in **Status Check**; omit the whole section if all four buckets are empty.

## Step 7: Confirm to the user

Tell the user the file was created and give the path. Optionally note how many days had content and how many were skipped.

Show `The Short Version` back to the user in your reply — it is the part they are most likely to send onward, and the part most worth a second opinion. Flag anything you deliberately left out of it, and any number you had to soften into a phrase.

If any files are "Ready to archive", remind the user that archival is manual and ask whether to move them to `notes/Archive/` (only terminal-state files — `done` plans, `resolved`/`wontfix` bugs and investigations — per the convention). Never move files automatically.

---

## Notes on judgment

The condensation step is where quality is made. Prefer grouping by theme or project rather than by day. For example:
- "Debugged the `user_role` schema mismatch in the `accounts_info` endpoint and identified the fix" is better than three separate bullets about reading the code, tracing the route, and identifying the root cause.
- "Migrated daily note skills to nested directory structure and validated with eval suite" is better than listing each skill individually.

When in doubt, keep the bullet that answers "what changed / what was decided" and drop the one that answers "what steps did I take".

A dense week is not a licence to write a long note. When there is genuinely more work than fits,
group harder and lean on wikilinks — the weekly is an index to the week, not a record of it. The
daily logs and the spun-out notes are the record.

The two audiences pull in opposite directions, and that is fine. `Done This Week` is allowed to be
dense, technical and specific — that is what makes it useful a month later. `The Short Version` is
allowed to be almost lossy, because a manager who reads six plain sentences and comes away with the
right impression of the week has got everything they needed. Do not let either one drag the other
toward the middle: a Short Version padded with detail stops being readable in 20 seconds, and a
Done This Week flattened into plain English stops being worth writing down.
