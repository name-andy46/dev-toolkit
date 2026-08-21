---
name: spec-apply
description: >-
  Drive the implementation of a proposed spec change: work its tasks.md checklist, keep the delta
  spec(s) in sync with what the implementation actually reveals, and move the change to status
  "applying". Use whenever the user wants to start building / implementing a change that was proposed
  with spec-propose. Triggers on "start implementing X", "apply the change", "let's build X", "work the
  tasks for X", "start on the <change-id> change". Part of the spec-workflow set (spec-propose →
  spec-apply → spec-verify → spec-archive). Runs the deterministic validator as a SOFT gate — reports
  issues but does not block mid-implementation, since a change is legitimately incomplete while in flight.
---

# spec-apply

Take a `proposed` change into implementation. This skill is the bridge between the spec and the code:
it drives `tasks.md`, and — crucially — keeps the delta spec honest as the real requirements emerge.

The validator is at `$SKILL/../../scripts/validate_specs.py` (`$SKILL` = the base dir shown to you when
the skill loads). It is Python 3.7+ stdlib-only — nothing to install. The examples below say `python3`;
on Windows that name often doesn't exist, so use `python` or `py -3` there.

## Step 1: Load the change

Resolve the change-id (ask if ambiguous) and read `docs/changes/<change-id>/` — `proposal.md`,
`tasks.md`, `design.md` (if present), and the delta spec(s) under `specs/`. Understand what the change
is supposed to do before touching anything.

## Step 2: Set status and baseline the validator

Set `proposal.md` frontmatter `status: applying`. Then run the validator as a **soft gate**:

```bash
python3 "$SKILL/../../scripts/validate_specs.py" --change <change-id>
```

Report anything it flags, but **do not hard-block** — an in-flight change may legitimately have open
tasks or a delta that's still being shaped. The gate is informational here; the hard gate is at archive.

## Step 3: Work the tasks

Implement against `tasks.md`. Check items off (`- [x]`) only when they are genuinely done. If the work
surfaces new sub-tasks, add them as unchecked items rather than silently skipping.

## Step 4: Keep the delta spec in sync (the important part)

Implementation almost always reveals that a requirement was slightly wrong, under-specified, or that a
scenario was missing. When it does, **update the delta spec to match reality** — that's the whole point
of a living spec:

- a requirement's statement changed → edit it (keep its `**Type:**`).
- a new behaviour appeared → add a `### Requirement:` with the right Type and a GIVEN/WHEN/THEN scenario.
- a MODIFIED/REMOVED requirement must still name one that exists in `docs/specs/<capability>/spec.md`.

Don't let the spec and the code drift. A change whose delta no longer describes what was built is worse
than no spec.

## Step 5: Re-check before handing off

Re-run the validator and report the current state. When the implementation is complete and the tasks are
done, point the user at **spec-verify** to check it properly before archiving. Leave `status: applying`
until verify.

## Boundary

This skill implements and keeps the delta spec current; it does **not** set `verified`, merge the delta
into the source specs, or archive — those are spec-verify and spec-archive. Architectural decisions go
under `## Decisions` in the change's `design.md` (see spec-propose), never into the spec itself.
