# Change lifecycle

A change moves through four states, tracked in the `status:` frontmatter of its `proposal.md`. Each
transition is gated by one skill; the validator (`validate_specs.py`) is the deterministic check behind
the gates.

```
proposed  --(spec-apply)-->  applying  --(spec-verify)-->  verified  --(spec-archive)-->  archived
```

| status | set by | meaning | gate |
|--------|--------|---------|------|
| `proposed` | **spec-propose** | change scaffolded (`proposal.md` + `tasks.md` + delta spec(s)); no implementation yet | — |
| `applying` | **spec-apply** | implementation in progress; `tasks.md` being worked; delta specs kept in sync with reality | **soft** — validator runs, violations reported, not blocked mid-implementation |
| `verified` | **spec-verify** | validator clean **and** a human/agent judgment review passed (scenarios meaningful, design coherent, tasks real) | validator must be clean before `verified` is set |
| `archived` | **spec-archive** | delta merged into the source specs, change moved to `docs/changes/archive/<id>/` | **hard** — `validate_specs.py --change <id> --archive` must pass (incl. no unchecked tasks) or archive is refused |

## The gates in detail

- **spec-apply (soft gate).** Runs the validator before declaring work started and sets `status: applying`.
  Reports violations but does **not** hard-block — a change is legitimately incomplete while being
  implemented. It keeps the delta specs honest as implementation reveals what the requirements really are.

- **spec-verify (clean-required).** Runs the validator and reports every violation. Only sets
  `status: verified` when the validator is clean *and* the judgment-level review the script can't do
  (are the scenarios meaningful? is the design coherent? are the tasks real work?) passes.

- **spec-archive (hard gate).** Runs `validate_specs.py --change <id> --archive`, which additionally
  fails on any unchecked `- [ ]` in `tasks.md`. Refuses to archive on any failure. On success it merges
  `ADDED`/`MODIFIED` requirements into `docs/specs/<capability>/spec.md`, drops `REMOVED` ones,
  moves the change under `docs/changes/archive/<id>/`, and sets
  `status: archived`.

## The artifact chain

The `status` above is the change's *lifecycle* state. Orthogonal to it, the four **planning artifacts**
inside a change form a **dependency chain** — each can only be written once the one it depends on
exists:

```
proposal ──► delta-specs ──► design (optional) ──► tasks
```

Each artifact is in one of three states:

| artifact | state → done | ready when | blocked until |
|----------|--------------|------------|---------------|
| `proposal.md` | file exists | always (chain root) | — |
| `specs/<capability>.md` | ≥1 delta file with ≥1 well-formed requirement | proposal done | proposal |
| `design.md` (optional) | file exists (or explicitly skipped) | proposal done | proposal |
| `tasks.md` | ≥1 task item | delta-specs done | delta-specs |

The validator renders this chain in its read-only **`status` mode** (`validate_specs.py status --change
<id>`) — presence-and-well-formedness only, **always exits 0**, never a gate. Use it to see at a glance
what a change still needs. The **design** step is where an architectural decision gets written down,
under `## Decisions` in `design.md`. The lifecycle gates (soft / clean / hard) live in spec-apply /
spec-verify / spec-archive.
