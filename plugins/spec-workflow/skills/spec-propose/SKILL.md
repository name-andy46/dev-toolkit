---
name: spec-propose
description: >-
  Start a spec-driven change in a code repository: scaffold a change proposal (proposal.md,
  optional design.md, tasks.md, and delta spec(s)) under docs/changes/<change-id>/, and bootstrap the
  docs/specs/ + docs/changes/ trees the first time (with confirmation). Use whenever the user wants to
  propose or draft a change, spec something out, or open a new change/proposal before implementing.
  Triggers on "propose a change", "spec out X", "let's spec X", "new change for X", "draft a proposal
  for X", "write a spec for this feature", "I want to add/modify/remove requirement X". Part of the
  spec-workflow set — hand off to spec-apply (implement), spec-verify (check), spec-archive
  (finalize). Architectural decisions are recorded in the change's own design.md, not in the spec.
---

# spec-propose

Turn an intent ("we should add rate-limiting to the ingest API") into a structured, reviewable **change**
under `docs/` — a proposal plus the delta spec(s) describing what it does to the service's requirements.
This is the front door of the `spec-workflow` set. It writes files but changes no code.

Bundled templates live in **this skill's own directory** — call it `$SKILL` (the base dir shown to you
when the skill loads). Read them from `$SKILL/../../assets/templates/…`; the deterministic validator is
`$SKILL/../../scripts/validate_specs.py`. Don't hardcode absolute paths. It is Python 3.7+ stdlib-only —
nothing to install; invoke it with `python3`, or `python` / `py -3` on Windows.

## Step 1: Bootstrap the trees (first time only, confirm first)

The specs live in your repo under `docs/`:

```
docs/
  specs/
    README.md               # capability index (seeded from assets/specs-index.md)
    <capability>/spec.md     # source of truth per capability
  changes/
    <change-id>/             # proposals in flight
    archive/<change-id>/     # completed changes
```

If `docs/specs/` or `docs/changes/` is absent, this repo hasn't used the workflow yet. **Tell the user
what you'll create and get an explicit yes before writing** (a one-time bootstrap):

```
No specs workflow found. I can start one under docs/:
  docs/specs/README.md   — capability index (seeded)
  docs/changes/          — where change proposals live
Create it? (yes / adjust)
```

On confirmation, read `$SKILL/../../assets/specs-index.md` → write `docs/specs/README.md`, and create the
`docs/changes/` directory. If a stray `docs/specs/` or `docs/changes/` already exists, read what's there
and report it before touching anything.

## Step 2: Pick the change id and capability

- **change-id** — a short kebab-case slug for the change (`add-ingest-rate-limit`, `drop-legacy-auth`).
  Confirm it with the user; it names `docs/changes/<change-id>/`.
- **capability** — the area of behaviour being changed. It maps to `docs/specs/<capability>/spec.md`.
  A change may touch more than one capability (one delta file each). If the source spec for a MODIFIED /
  REMOVED requirement doesn't exist yet, say so — you can only MODIFY/REMOVE something already specced.

## Step 3: Scaffold the change

Create `docs/changes/<change-id>/` from the templates in `$SKILL/../../assets/templates/`:

- `proposal.md` — fill the title, Why, What, Scope; set frontmatter `status: proposed` and the change-id.
- `tasks.md` — the implementation checklist (leave real, unchecked `- [ ]` items).
- `specs/<capability>.md` — one delta spec per capability. Each `### Requirement:` gets **exactly one**
  `**Type:** ADDED | MODIFIED | REMOVED`; every ADDED/MODIFIED requirement gets ≥1 `#### Scenario:` with
  GIVEN / WHEN / THEN. (See `$SKILL/../../references/spec-format.md`.)
- `design.md` — only if the change needs a technical approach; otherwise skip it.

Present the drafted files for review before writing. Write only after the user is happy.

## Step 4: Architectural decisions → `design.md`

If the change carries a real architectural decision — a framework, pattern, data-model or auth choice
with a trade-off — record it under a `## Decisions` heading in the change's `design.md`, **not** in the
delta spec. The split matters: a spec says *what the software must do*, a decision says *why it was
built that way*. Mixed together, both get harder to read six months later.

Each decision needs three things: the choice, the alternatives weighed, and the consequence accepted.
A paragraph is usually enough. Link it from `proposal.md` so someone starting there finds it.

**Never silently drop a decision.** If there's no `design.md` yet, create one — this is what it's for.

## Step 5: Sanity-check

Run the validator on the new change and report anything it flags (a fresh proposal should be clean):

```bash
python3 "$SKILL/../../scripts/validate_specs.py" --change <change-id>
```

Leave `status: proposed`. Point the user at **spec-apply** to start implementing.

## Boundary

This skill scaffolds and proposes — it does not implement, verify, or archive, and it never edits
code.
