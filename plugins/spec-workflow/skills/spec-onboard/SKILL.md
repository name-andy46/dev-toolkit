---
name: spec-onboard
description: >-
  Interactive, no-stakes tutorial that teaches the whole spec-driven workflow using the user's ACTUAL
  repo: find one small real improvement and walk it through spec-propose → spec-apply →
  spec-verify → spec-archive, defining each term inline the first time it appears (spec, capability,
  change, delta, GIVEN/WHEN/THEN scenario). For anyone new to the whole idea. Creates nothing
  without confirmation at each step. Triggers on "walk me through the spec workflow", "onboard me to
  specs", "teach me how to use the spec skills", "give me a spec-workflow tutorial", "explain the spec
  workflow with an example". It teaches by driving the real skills — it is not itself spec-propose/apply/
  archive. Part of the spec-workflow set.
---

# spec-onboard

A guided, hands-on tour of the spec workflow, run on the user's own repo so it sticks. The goal is
teaching, not throughput: go slowly, define every term the first time it appears, and **write nothing
without an explicit yes at each step**. At the end the practice change can be kept or thrown away — the
user's call. This skill doesn't add mechanics; it drives the real base skills and narrates them.

## Step 0: Set expectations and sketch the model

Tell the user this is a no-stakes walkthrough on a tiny real change, and that nothing gets written
without their confirmation. Sketch the model in a few lines, defining terms as you introduce them:

- **spec** — the source-of-truth requirements for a **capability** (an area of behaviour), living at
  `docs/specs/<capability>/spec.md`.
- **change** — a proposal that edits the specs, tracked under `docs/changes/<change-id>/` as **delta**
  specs (what it ADDs / MODIFIEs / REMOVEs) plus a proposal, optional design, and tasks.
- the four states a change moves through: `proposed → applying → verified → archived`.

## Step 1: Find one small real improvement (read-only)

Scan the repo read-only for a genuinely small, low-stakes improvement to spec out — a tiny missing
validation, a small config default, a minor endpoint tweak. Offer one or two candidates and let the user
pick. Keep it small enough to finish the whole loop quickly. If the repo hasn't adopted the workflow yet,
explain that the first run bootstraps `docs/specs/` + `docs/changes/`, and that it confirms first.

## Step 2: Walk the loop, one skill per phase

Drive the real skills, pausing at each phase to define the term, show the artifact, and confirm before
any write. Show the chain readout between phases so the dependency chain is concrete:

```bash
python3 "$SKILL/../../scripts/validate_specs.py" status --change <change-id>
```

1. **Propose** — use **spec-propose** to scaffold the change. Define **delta spec**, the
   **`**Type:**` tag**, and the **GIVEN/WHEN/THEN scenario** as they first appear.
2. **Apply** — use **spec-apply**: define the soft gate, work a task or two, show how the delta spec is
   kept in sync with reality.
3. **Verify** — use **spec-verify**: define the difference between the deterministic validator and the
   judgment review; show a clean validator run.
4. **Archive** — use **spec-archive**: define the hard `--archive` gate, and show the delta merging into
   the source spec.

## Step 3: Define where a decision goes, if one comes up

If the practice change surfaces a real architectural decision (at the design step), teach the split: a
**spec** says what the software must do; a **decision** says why it was built that way, and it belongs
under `## Decisions` in the change's `design.md`, linked from `proposal.md`. If no genuine decision
arises, name the distinction and move on — don't manufacture one.

## Step 4: Keep it or bin it

At the end, offer a clean choice:

- **keep it** — finish archiving properly so the practice change becomes a real, merged spec; or
- **bin it** — delete the `docs/changes/<change-id>/` folder (and undo any bootstrap the user doesn't
  want) so the repo is exactly as it was.

Confirm which, and act only on their answer.

## Boundary

This skill teaches by driving the other spec-workflow skills; it introduces no new artifacts or
mechanics and writes nothing without per-step confirmation. It never touches code beyond the tiny
practice change the user approves.
