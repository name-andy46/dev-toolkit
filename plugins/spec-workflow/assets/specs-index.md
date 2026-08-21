# Specifications

The source of truth for this service's current, accepted requirements. Each capability has its own
spec under `<capability>/spec.md`. Changes are proposed as delta specs under `docs/changes/` and merged
here when archived (see the `spec-workflow` plugin).

| Capability | Spec | Summary |
|------------|------|---------|
| _none yet_ | | |

## How this works

- **Source specs** (`docs/specs/<capability>/spec.md`) — the accepted requirements, right now.
- **Changes** (`docs/changes/<change-id>/`) — proposals in flight: `proposal.md`, optional `design.md`,
  `tasks.md`, and delta spec(s) under `specs/`.
- **Decisions** — the reasoning behind a change lives with the change, under `## Decisions` in its
  `design.md`. A spec says what the software must do; a decision says why it was built that way.

Propose a change with **spec-propose**, implement with **spec-apply**, check with **spec-verify**, and
finalize with **spec-archive** (which merges the delta into these source specs).
