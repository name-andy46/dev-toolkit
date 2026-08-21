---
name: spec-recall
description: >-
  Look up a repo's specs and changes: search docs/specs/ and docs/changes/ (including archive) to
  answer what the current spec for a capability is, the status of a change, or which changes touch a
  given area. Use whenever the user asks about the spec/requirements for something, the
  state of a change, or wants to find changes affecting an area — before scanning the codebase. Triggers
  on "what's the spec for X", "what do our specs say about X", "status of change Y", "which changes touch
  Z", "is there a change for X", "what requirements do we have for X", "show me the spec/change for X".
  Part of the spec-workflow set. For "why did we decide…" questions, read the change's design.md,
  which is where decisions are recorded.
---

# spec-recall

The read/recall counterpart to the rest of the workflow — the `notes-recall` analogue for a repo's
**project specs**. Answer from the `docs/` trees first; only fall back to a code scan if the docs don't
have it.

## What lives where

```
docs/
  specs/<capability>/spec.md      # current accepted requirements (source of truth)
  specs/README.md                 # capability index
  changes/<change-id>/            # active proposals: proposal.md (status), tasks.md, specs/<cap>.md
  changes/archive/<change-id>/    # completed changes
```

If `docs/specs/` and `docs/changes/` don't exist, this repo hasn't adopted the workflow — say so and
offer **spec-propose** to start it.

## Search ladder

Run in order; stop as soon as you can answer.

1. **Capability index** — `docs/specs/README.md`. Fastest route from a topic to a capability spec.
2. **Source spec (exact/substring)** — `ls docs/specs/` for a matching `<capability>/`, then read
   `docs/specs/<capability>/spec.md`. This is the authoritative "what's the spec for X".
3. **Active changes** — `ls docs/changes/` for a matching `<change-id>/`; read its `proposal.md`
   (the `status:` frontmatter answers "what's the state of Y") and its delta spec(s).
4. **Archived changes** — `ls docs/changes/archive/` for completed changes touching the subject.
5. **Content grep (bounded)** — `grep -rin "<subject>" docs/specs docs/changes` to find requirements or
   changes mentioning the subject when the name didn't match a path.
6. **Decisions** — for "why is it this way", read the change's `design.md` (`## Decisions`) and its
   proposal's Why. The spec says what the software must do; the reasoning lives with the change.

## Answering

Questions map to sources:

- **"What's the spec for X?"** → the source spec (`docs/specs/<capability>/spec.md`) — summarize the
  requirements and scenarios; cite `file:line`.
- **"Status of change Y?"** → `docs/changes/Y/proposal.md` `status:` + open items from its `tasks.md`.
- **"Which changes touch Z?"** → grep active + archived changes; list the change-ids and their statuses.
- **"Why is X designed this way?"** → the change's `design.md` (`## Decisions`), then its Why.

Synthesize — don't paste whole files. Cite paths so the user can jump to them. If active and archived
sources conflict (a change claims a requirement the source spec doesn't have), surface the conflict
rather than picking one silently.

## Boundary

Read-only. This skill looks things up; it doesn't propose, apply, verify, or archive.
