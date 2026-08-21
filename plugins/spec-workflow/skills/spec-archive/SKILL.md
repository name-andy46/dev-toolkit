---
name: spec-archive
description: >-
  Finalize a completed spec change: hard-gate on the deterministic validator (validate_specs.py --archive,
  which also fails on unchecked tasks), then merge the change's ADDED/MODIFIED requirements into the
  source specs under docs/specs/, drop REMOVED ones, move the change to docs/changes/archive/, and set
  status "archived". Use whenever the user says a change is done and wants to merge/finalize/archive it.
  Triggers on "archive the change", "X is done, merge it", "finalize the spec for X", "the <change-id>
  change is complete", "fold X into the specs". Part of the spec-workflow set (spec-propose →
  spec-apply → spec-verify → spec-archive). Refuses to archive if the change doesn't validate.
---

# spec-archive

The end of the workflow: fold a finished change's delta into the source-of-truth specs and retire it.
This is a **hard gate** — a change that doesn't validate (or still has open tasks) does not get archived.

The validator is at `$SKILL/../../scripts/validate_specs.py` (`$SKILL` = the base dir shown to you when
the skill loads). It is Python 3.7+ stdlib-only — nothing to install. The examples below say `python3`;
on Windows that name often doesn't exist, so use `python` or `py -3` there.

## Step 1: Hard gate — validate with `--archive`

```bash
python3 "$SKILL/../../scripts/validate_specs.py" --change <change-id> --archive
```

The `--archive` flag additionally enforces that `tasks.md` has **no unchecked `- [ ]` items**. If the
validator exits non-zero, **stop** — report the violations and refuse to archive. Do not merge a change
that fails its gate, and do not hand-wave past unchecked tasks.

## Step 2: Merge the delta into the source specs

For each delta spec `docs/changes/<change-id>/specs/<capability>.md`, apply it to
`docs/specs/<capability>/spec.md` per each requirement's `**Type:**`:

- **ADDED** — insert the requirement (and its scenarios) into the source spec. If the source spec file
  doesn't exist yet, create `docs/specs/<capability>/spec.md` (with a `# <Capability> Specification` +
  `## Purpose`) and add the capability to `docs/specs/README.md`.
- **MODIFIED** — replace the same-named requirement in the source spec with the delta's version.
- **REMOVED** — delete the same-named requirement (and its scenarios) from the source spec.

Drop the `**Type:**` tags in the merged source spec — they only belong in deltas. Preserve the source
spec's other requirements and its `## Purpose`.

## Step 3: Settle the decisions

If the change recorded anything under `## Decisions` in `design.md`, it travels with the change into
the archive, so the reasoning stays reachable from the merged spec rather than being buried in an
archived folder. The cross-links that make it reachable are exactly what the move is about to break —
Step 4 repairs them.

## Step 4: Archive the change

- Set the change's `proposal.md` frontmatter `status: archived`.
- Move the whole change directory to `docs/changes/archive/<change-id>/` (create `docs/changes/archive/`
  if needed). Use `git mv` when the repo tracks it so history follows.
- **Repair the relative links the move just broke — in both directions.** The change is now one
  directory deeper, and every markdown relative link resolves from the file that contains it, so a
  single move invalidates links pointing *out of* the change and links pointing *into* it. This is not
  optional and it is not occasional: it fires on every archive, and an archive that leaves dead links
  has silently damaged the cross-references this workflow exists to maintain.

  **Outbound** — inside `docs/changes/archive/<change-id>/`, every `../` link needs one more level:

  | was | becomes |
  |---|---|
  | `../../specs/<cap>/spec.md` | `../../../specs/<cap>/spec.md` |
  | `../../adr/NNNN-….md` | `../../../adr/NNNN-….md` |
  | `../<other-active-change>/proposal.md` | `../../<other-active-change>/proposal.md` |
  | `../archive/<other>/proposal.md` | `../<other>/proposal.md` *(both are under `archive/` now)* |

  That last row is the one that trips people up: a link to an **already-archived sibling** *loses* a
  level instead of gaining one, because both ends now sit under `archive/`.

  **Inbound** — anything pointing at the change needs an `archive/` segment inserted. Search the whole
  of `docs/`, not just the active changes:

  ```bash
  grep -rn "changes/<change-id>/" docs/ --include=*.md
  ```

## Step 5: Confirm clean

Re-run the validator over all active changes **with `--strict-links`**, which adds a sweep of every
relative link under `docs/` and exits non-zero if any is dead:

```bash
python3 "$SKILL/../../scripts/validate_specs.py" --strict-links
```

The plain per-change checks are change-scoped and cannot see this class of breakage — the change you
just moved is archived (therefore out of scope), and `docs/specs/`, `docs/adr/`, and previously-archived
changes are never in scope at all. `--strict-links` is what closes that gap; a clean exit without it
says nothing about the links you just moved.

The sweep always prints a `link sweep: N file(s) scanned under docs/, M broken relative link(s)` line.
**Read the file count, not just the zero** — a sweep that scanned nothing reports the same `0 broken` as
one that found nothing. If N looks implausibly small, you are not at the repository root.

If the sweep reports a dead link that predates this archive and is unrelated to it, say so explicitly
rather than quietly leaving it — don't fold an unrelated repair into the archive without flagging it.

Report the final result: what merged into which source specs, where the change now lives, and how many
links were repaired.

## Boundary

This skill is the only one that writes to `docs/specs/` and moves changes to `archive/`. It never
touches code.
