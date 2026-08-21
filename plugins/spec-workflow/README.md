# spec-workflow

Decide what the software should do *before* it's built, in writing you can read — then keep that
writing true as it gets built.

This is for anyone building an application with Claude who can't audit the code. You can't review a
diff, but you *can* review a sentence like *"WHEN a symbol has fewer than 200 bars, THEN it is
excluded from the screen and reported"*. That sentence is a **requirement**, and this plugin keeps a
set of them under `docs/` in plain markdown: proposed as a change, implemented against a checklist,
verified, and merged into a source of truth. A deterministic Python validator enforces the structure
so the paperwork can't quietly rot.

Nothing here needs npm, a CLI, or a service. It's markdown files and one stdlib Python script.

## New to this? Start there

```
walk me through the spec workflow
```

`spec-onboard` runs the whole loop on a tiny real improvement in your own repo, defining every term
the first time it appears, and writing nothing without asking. At the end you keep the practice
change or throw it away. It's the cheapest way to learn the vocabulary, which is the only genuinely
steep part of this.

## The loop

```
spec-propose  →  spec-apply  →  spec-verify  →  spec-archive
   (draft)       (implement)      (check)       (merge + retire)
                                                spec-recall  (look things up, any time)
```

| Skill | What it does | Gate |
|-------|--------------|------|
| **spec-onboard** | guided tutorial that drives the whole loop on your repo, defining terms inline | writes nothing unconfirmed |
| **spec-propose** | bootstrap `docs/` (confirm-first) and scaffold `docs/changes/<id>/`; sets `status: proposed` | — |
| **spec-apply** | drive `tasks.md`, keep the spec honest as implementation reveals reality; `status: applying` | soft — validator informs, doesn't block |
| **spec-verify** | validator **plus** the judgment review a script can't do; `status: verified` only when clean | validator must be clean |
| **spec-archive** | merge the change into `docs/specs/`, move it to `archive/`; `status: archived` | **hard** — refuses if it doesn't validate |
| **spec-recall** | answer "what's the spec for X", "status of Y", "which changes touch Z" | read-only |

## The vocabulary (four words)

- **capability** — an area of behaviour, e.g. `screening`, `data-fetch`. Each has one spec.
- **spec** — the accepted requirements for a capability, as they stand right now, at
  `docs/specs/<capability>/spec.md`.
- **change** — a proposal to alter the specs, under `docs/changes/<change-id>/`.
- **delta spec** — what a change *does* to requirements: each one tagged `ADDED`, `MODIFIED` or
  `REMOVED`. On archive, the deltas fold into the source spec and the change retires.

Requirements carry **scenarios** in GIVEN / WHEN / THEN form. That's the part worth the effort: a
scenario is a sentence you can check against the running software without reading a line of code.

## The layout it manages

```
docs/
  specs/                         # source of truth
    README.md                    #   capability index
    <capability>/spec.md
  changes/                       # changes in flight
    <change-id>/                 #   proposal.md, design.md (opt), tasks.md, specs/<capability>.md
    archive/<change-id>/         #   completed changes
```

`spec-propose` creates these lazily, only after showing you what it will write and getting a yes.
See `references/spec-format.md` for the format and `references/change-lifecycle.md` for the states
and gates.

## Where decisions go

A spec says *what the software must do*. A **decision** says *why it was built that way* — which
library, which pattern, which trade-off — and that goes under `## Decisions` in the change's
`design.md`, linked from its `proposal.md`. Keeping the two apart is deliberate: mixed together,
both get harder to read later. The outcome of a decision is usually recoverable from the code; the
alternative you rejected never is, so it's the part most worth writing down.

## The validator

`scripts/validate_specs.py` — Python 3, standard library only, read-only. It enforces *structure*:
files present, exactly one `**Type:**` per delta requirement, `MODIFIED`/`REMOVED` naming a
requirement that actually exists, `ADDED`/`MODIFIED` carrying scenarios with GIVEN/WHEN/THEN, links
resolving — per change *and* across the whole `docs/` tree, see below — and (at the archive gate) no
unchecked tasks.

It makes **no judgment about merit** — whether a requirement is *right* is yours and `spec-verify`'s
call, never the script's. It no-ops with exit 0 in any repo without `docs/changes/`, so it's safe
anywhere.

**Requirements: Python 3.7 or newer. Nothing else** — no pip install, no venv, no lockfile, no
vendored code. It imports only `argparse`, `os`, `re`, `subprocess`, `sys` and `pathlib`, all from the
standard library, and it never writes a file. Linux, macOS and Windows behave identically; on Windows
use `python` or `py -3` in place of `python3`, which frequently isn't installed under that name.

```bash
python3 scripts/validate_specs.py --change <id>            # one change
python3 scripts/validate_specs.py                          # all active changes
python3 scripts/validate_specs.py --change <id> --archive  # + the hard archive gate
python3 scripts/validate_specs.py --strict-links           # + gate on dead links anywhere under docs/
python3 scripts/validate_specs.py status --change <id>     # what's done / still missing; always exit 0
```

### The link sweep (check 8)

Most checks are **change-scoped**, and the change list deliberately excludes `archive/`. That leaves a
blind spot with teeth: archiving moves a change one directory deeper, which breaks its outbound `../`
links *and* every inbound link pointing at it — and none of those files are in scope for a per-change
check afterwards. Check 8 walks every `*.md` under `docs/` instead, so it sees source specs, decision
records, and archived changes too, and it keeps working when someone archives, renames, or moves a
file by hand.

It runs on every validation invocation and prints a one-line summary to stdout:

```
link sweep: 42 file(s) scanned under docs/, 0 broken relative link(s)
```

The **file count is part of the signal** — `0 broken` out of `0 scanned` is not a clean bill of health.
Findings are warnings by default (visible, non-blocking, so a pre-existing dead link elsewhere in
`docs/` can't block an unrelated change); `--strict-links` promotes them to violations. `spec-archive`
passes it after the move.

## Configuration

None. The skills find your repo root via `$CLAUDE_PROJECT_DIR`, the git top level, or the working
directory, in that order.

## Install

```bash
claude plugin install spec-workflow@dev-toolkit
```

Start a new Claude Code session so the skills load, then say *"walk me through the spec workflow"*.
