# Spec & delta-spec format

The formats the `spec-workflow` skills write and the `validate_specs.py` validator enforces. The
validator is **structural only** — it checks presence and well-formedness, never whether a
requirement is *correct* or a scenario *meaningful*. Those are the skills' (and the reviewer's) job.

## Source-of-truth spec — `docs/specs/<capability>/spec.md`

The current, accepted requirements for one capability. This is what a change's delta specs merge into
when the change is archived.

```markdown
# <Capability> Specification

## Purpose
<1-2 sentences: what this capability is for.>

### Requirement: <short name>
<statement — SHALL / MUST phrasing encouraged>

#### Scenario: <short name>
- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>
```

- Requirements are `### Requirement: <name>` headings; scenarios are `#### Scenario: <name>` nested
  under them. A requirement owns every scenario until the next `###` (or higher) heading.
- The **requirement name** is the identity used to match a delta's MODIFIED/REMOVED against the source,
  so keep names stable and unique within a capability.

## Delta spec — `docs/changes/<change-id>/specs/<capability>.md`

What one change proposes to *do* to a capability's requirements. Same requirement/scenario anchors as
the source spec, plus a required **Type** tag per requirement. The `<capability>` filename maps directly
to `docs/specs/<capability>/spec.md`.

```markdown
# <Capability> — delta for <change-id>

### Requirement: <name>
**Type:** ADDED            # exactly one of ADDED | MODIFIED | REMOVED
<statement>

#### Scenario: <name>
- GIVEN ...
- WHEN ...
- THEN ...
```

## Rules the validator enforces

1. Each active `docs/changes/<id>/` has a `proposal.md` (with a `status:` in frontmatter) and a `tasks.md`.
2. Every delta `### Requirement:` has **exactly one** `**Type:**` (one of `ADDED` | `MODIFIED` | `REMOVED`).
3. A `MODIFIED` or `REMOVED` requirement must name a requirement that **already exists** in the matching
   source spec (`docs/specs/<capability>/spec.md`).
4. Every `ADDED` or `MODIFIED` requirement has **≥1 scenario**, and each scenario contains a `GIVEN`, a
   `WHEN`, and a `THEN` line (case-insensitive; a leading `- `/`* ` bullet is fine). `REMOVED` needs none.
5. Relative markdown links inside the change's files resolve to existing paths.
6. (Archive gate only) `tasks.md` has no unchecked `- [ ]` items.
7. Any decision-record link of the form `docs/adr/NNNN-*.md` that a change references resolves to an
   existing file. This is a dangling-link check for repos that keep a separate decision log; these
   skills don't create one.

## Type semantics (what `spec-archive` does with each)

| Type | Meaning | On archive |
|------|---------|------------|
| `ADDED` | a brand-new requirement | inserted into the source spec |
| `MODIFIED` | an existing requirement changes | replaces the same-named requirement in the source spec |
| `REMOVED` | an existing requirement goes away | deleted from the source spec |

## Out of scope for the validator (skill / reviewer judgment)

Whether a requirement is correct, a design good, scenarios sufficient or meaningful, or the change worth
doing. The validator deliberately resists this scope creep — it proves structure, not merit.
