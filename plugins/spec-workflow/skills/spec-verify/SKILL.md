---
name: spec-verify
description: >-
  Verify a spec change is ready: run the deterministic validator (validate_specs.py) AND do the
  judgment-level review the script can't — are the scenarios meaningful, is the design coherent, are the
  tasks real work — then set status "verified" only when the change is clean. Use whenever the user asks
  to verify, check, or review a change, or asks whether a change is ready to archive/merge. Triggers on
  "verify the change", "check the spec for X", "is X ready", "review the <change-id> change", "does this
  change validate". Part of the spec-workflow set (spec-propose → spec-apply → spec-verify →
  spec-archive). This is the quality gate before archiving; it does not merge or archive.
---

# spec-verify

The quality gate. It combines the **deterministic** check (structure, via the validator) with the
**judgment** check (does the spec actually mean anything) that a script can't make — and only promotes a
change to `verified` when both pass.

The validator is at `$SKILL/../../scripts/validate_specs.py` (`$SKILL` = the base dir shown to you when
the skill loads). It is Python 3.7+ stdlib-only — nothing to install. The examples below say `python3`;
on Windows that name often doesn't exist, so use `python` or `py -3` there.

## Step 1: Deterministic check

```bash
python3 "$SKILL/../../scripts/validate_specs.py" --change <change-id>
```

Report every violation it prints, grouped as it groups them (`CHECK n: <file>: <detail>`). If it's not
clean, the change is **not** verifiable yet — surface the issues and stop before setting status.

## Step 2: Judgment review (what the validator deliberately won't do)

The validator proves structure, not merit. Do the review it can't:

- **Scenarios meaningful?** Do GIVEN/WHEN/THEN describe real, testable behaviour — or are they
  placeholder filler that happens to contain the three keywords?
- **Requirements right?** Does each requirement actually capture what the change does? Is the `Type`
  (ADDED/MODIFIED/REMOVED) correct against the source spec?
- **Design coherent?** If there's a `design.md`, does the approach match the requirements and the code?
- **Tasks real?** Is `tasks.md` genuine implementation work, and does it reflect what was built?
- **Decisions captured?** If the change made an architectural choice, is it written under
  `## Decisions` in `design.md`? Flag a decision that went unrecorded — it's the part nobody can
  reconstruct later.

Report findings plainly. Prefer concrete pointers (`file:line`) over vague notes.

## Step 3: Set status

- **Clean (validator + judgment):** set `proposal.md` frontmatter `status: verified` and tell the user
  it's ready for **spec-archive**.
- **Not clean:** leave the status as-is (`applying`), list what needs fixing, and point back at
  spec-apply. Don't set `verified` on a change with open issues.

## Boundary

This skill verifies and sets `verified`; it does **not** merge the delta into the source specs or move
the change to archive — that's spec-archive, which re-runs the validator with its hard `--archive` gate.
