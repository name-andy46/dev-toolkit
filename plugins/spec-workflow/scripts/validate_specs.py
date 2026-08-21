#!/usr/bin/env python3
"""validate_specs.py — deterministic structural validator for the spec-workflow set.

Checks presence and well-formedness of change proposals and delta specs under a
service repo's docs/ tree. It makes NO semantic judgment — it never decides whether
a requirement is *correct*, a design is *good*, or scenarios are *sufficient* /
meaningful. It only verifies that the required files exist and that the
delta-spec / scenario structure is well-formed (presence-and-well-formedness only).

Read-only: never opens a file for writing.

Usage:
  validate_specs.py [--change ID] [--all] [--archive] [--strict-links] [--project-dir PATH]
  validate_specs.py status [--change ID] [--project-dir PATH]

  --change ID       validate only docs/changes/<ID>/ (a missing named change is an error).
  --all             validate all active (non-archived) changes — the default when
                    --change is omitted; accepted for explicitness, never pulls in
                    archived changes.
  --archive         additionally enforce check 6 (tasks.md has no unchecked items);
                    used by spec-archive as a hard gate.
  --strict-links    promote the tree-wide link sweep (check 8) from warnings to
                    violations, so a dead relative link anywhere under docs/ exits 1;
                    used by spec-archive after it moves a change into archive/.
  --project-dir P   the service repo root. Resolution precedence:
                    --project-dir -> $CLAUDE_PROJECT_DIR -> git rev-parse --show-toplevel -> CWD.

  status            informational mode: print the artifact-dependency-chain readout
                    (proposal -> delta-specs -> design[optional] -> tasks) for a change,
                    each artifact marked done / ready / blocked. Presence-and-well-formedness
                    only; never a gate. With --change, one change; without, all active ones.

Checks 1-7 are change-scoped. Check 8 is the exception: a tree-wide relative-link sweep over
docs/**/*.md that runs on every validation invocation, because the per-change checks go blind
the moment spec-archive moves a change into docs/changes/archive/. It always prints a one-line
"link sweep: N file(s) scanned under docs/, M broken relative link(s)" summary to stdout — the
file count is a deliberate guard, since a sweep that scanned nothing is otherwise
indistinguishable from one that found nothing.

Exit 0 = clean (also when docs/changes/ is absent — a safe no-op across non-spec repos);
         status mode ALWAYS exits 0 (it is informational, not a gate).
Exit 1 = one or more violations, printed to stderr grouped by check as
         "CHECK n: <path>: <detail>".
         Check 8 findings are WARN-only (stderr, exit 0) unless --strict-links promotes them.

Portability: Python 3.7+, standard library only — no pip install, no venv, nothing to
vendor. Runs the same on Linux, macOS and Windows. Invoke it with `python3`; on Windows,
where `python3` frequently does not exist, use `python` or `py -3`.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Force UTF-8 on stdout/stderr. Windows defaults them to the locale codepage (cp1252/cp437),
# which cannot encode the status readout's ✓/◆/○ or the em dashes in some messages — and when
# output is piped (how a skill always runs this) Python does NOT fall back to the console's
# UTF-16 path, so it raises UnicodeEncodeError mid-print. That turned an informational status
# run into a traceback and a non-zero exit, breaking this script's own "status always exits 0"
# contract. errors="replace" so an unencodable glyph degrades to '?' instead of killing a gate.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)   # absent <3.7 / on a replaced stream
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass                               # a stream that can't be reconfigured

# --- heading / structure -----------------------------------------------------
RE_HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*$')
RE_REQ_TAIL = re.compile(r'^Requirement:\s*(.+?)\s*$')
RE_SCEN_TAIL = re.compile(r'^Scenario:\s*(.+?)\s*$')
RE_TYPE = re.compile(r'^\s*\*\*Type:\*\*\s*(ADDED|MODIFIED|REMOVED)\b', re.IGNORECASE)
RE_GIVEN = re.compile(r'^\s*[-*]?\s*GIVEN\b', re.IGNORECASE)
RE_WHEN = re.compile(r'^\s*[-*]?\s*WHEN\b', re.IGNORECASE)
RE_THEN = re.compile(r'^\s*[-*]?\s*THEN\b', re.IGNORECASE)
# --- frontmatter / tasks / links --------------------------------------------
RE_FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)
RE_STATUS = re.compile(r'^\s*status:\s*\S', re.MULTILINE)
RE_UNCHECKED = re.compile(r'^\s*[-*]\s+\[\s\]\s')
RE_TASK = re.compile(r'^\s*[-*]\s+\[[ xX]\]\s')      # any checkbox task (checked or not)
RE_MDLINK = re.compile(r'\[[^\]]*\]\(\s*([^)\s]+?)\s*(?:\s+"[^"]*")?\)')
RE_SKIP_LINK = re.compile(r'^(?:[a-zA-Z][a-zA-Z0-9+.\-]*://|mailto:|tel:|//)')
RE_ADR = re.compile(r'(?:^|/)(\d{4}-[^/]*\.md)$')


class Scenario:
    __slots__ = ("name", "line", "body")

    def __init__(self, name, line):
        self.name = name
        self.line = line
        self.body = []


class Requirement:
    __slots__ = ("name", "line", "types", "scenarios")

    def __init__(self, name, line):
        self.name = name
        self.line = line
        self.types = []       # every ADDED/MODIFIED/REMOVED seen; counted, not asserted
        self.scenarios = []


class SpecDoc:
    __slots__ = ("path", "requirements")

    def __init__(self, path):
        self.path = path
        self.requirements = []


def project_dir(arg):
    """Resolve the service repo root: --project-dir -> $CLAUDE_PROJECT_DIR -> git toplevel -> CWD."""
    if arg:
        return Path(arg)
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True, stderr=subprocess.DEVNULL).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return Path.cwd()


def rel(root, p):
    """Display path relative to root when possible, else the path as-is."""
    try:
        return str(Path(p).relative_to(root))
    except Exception:
        return str(p)


def read_text_safe(p, root, violations):
    """Read a file, routing any I/O error to a CHECK 0 violation rather than crashing."""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        violations.append((0, "CHECK 0: %s: could not read file (%s)" % (rel(root, p), type(e).__name__)))
        return None


def parse_spec(text):
    """One stateful line-scan -> SpecDoc. A '### Requirement:' owns the '#### Scenario:'
    blocks under it until the next heading of level <= 3. '**Type:**' and GIVEN/WHEN/THEN
    are recorded, never asserted, here — the checks judge counts/presence."""
    doc = SpecDoc(None)
    cur_req = None
    cur_scen = None
    for i, line in enumerate(text.splitlines(), start=1):
        h = RE_HEADING.match(line)
        if h:
            level = len(h.group(1))
            rest = h.group(2)
            if level <= 3:
                cur_scen = None
                m = RE_REQ_TAIL.match(rest) if level == 3 else None
                if m:
                    cur_req = Requirement(m.group(1), i)
                    doc.requirements.append(cur_req)
                else:
                    cur_req = None       # any other <=3 heading closes the current requirement
            elif level == 4:
                cur_scen = None
                m = RE_SCEN_TAIL.match(rest)
                if m and cur_req is not None:
                    cur_scen = Scenario(m.group(1), i)
                    cur_req.scenarios.append(cur_scen)
                # a scenario with no owning requirement is orphaned -> dropped
            else:  # level 5-6: treat as body of the current scenario, if any
                if cur_scen is not None:
                    cur_scen.body.append(line)
            continue
        # non-heading line
        if cur_req is not None:
            mt = RE_TYPE.match(line)
            if mt:
                cur_req.types.append(mt.group(1).upper())
        if cur_scen is not None:
            cur_scen.body.append(line)
    return doc


def parse_deltas(change_dir, root, violations):
    """Return {capability: SpecDoc} for change_dir/specs/*.md (capability = filename stem)."""
    out = {}
    specs = change_dir / "specs"
    if not specs.is_dir():
        return out
    for f in sorted(specs.glob("*.md")):
        text = read_text_safe(f, root, violations)
        if text is None:
            continue
        doc = parse_spec(text)
        doc.path = f
        out[f.stem] = doc
    return out


def source_names(specs_dir, capability, cache, root, violations):
    """Memoized set of requirement names in docs/specs/<capability>/spec.md.
    Returns None if that source spec file does not exist."""
    if capability in cache:
        return cache[capability]
    src = specs_dir / capability / "spec.md"
    if not src.exists():
        cache[capability] = None
        return None
    text = read_text_safe(src, root, violations)
    names = set() if text is None else {r.name for r in parse_spec(text).requirements}
    cache[capability] = names
    return names


# --- checks ------------------------------------------------------------------
def check1(change_dir, root, violations):
    proposal = change_dir / "proposal.md"
    tasks = change_dir / "tasks.md"
    if not proposal.exists():
        violations.append((1, "CHECK 1: %s: missing proposal.md" % rel(root, change_dir)))
    else:
        text = read_text_safe(proposal, root, violations)
        if text is not None:
            fm = RE_FRONTMATTER.match(text)
            block = fm.group(1) if fm else "\n".join(text.splitlines()[:20])
            if not RE_STATUS.search(block):
                violations.append((1, "CHECK 1: %s: no 'status:' in frontmatter" % rel(root, proposal)))
    if not tasks.exists():
        violations.append((1, "CHECK 1: %s: missing tasks.md" % rel(root, change_dir)))


def check2(deltas, root, violations):
    for doc in deltas.values():
        for req in doc.requirements:
            n = len(req.types)
            if n == 0:
                violations.append((2, 'CHECK 2: %s: requirement "%s" (line %d) has no **Type:** tag '
                                      '(expected exactly one of ADDED|MODIFIED|REMOVED)'
                                   % (rel(root, doc.path), req.name, req.line)))
            elif n >= 2:
                violations.append((2, 'CHECK 2: %s: requirement "%s" (line %d) has %d **Type:** tags '
                                      '(expected exactly one)'
                                   % (rel(root, doc.path), req.name, req.line, n)))


def check3(deltas, specs_dir, cache, root, violations):
    for cap, doc in deltas.items():
        for req in doc.requirements:
            if len(req.types) != 1:
                continue                       # check 2 already reported the count
            t = req.types[0]
            if t not in ("MODIFIED", "REMOVED"):
                continue                       # ADDED has no source counterpart, by design
            names = source_names(specs_dir, cap, cache, root, violations)
            if names is None:
                violations.append((3, 'CHECK 3: %s: %s requirement "%s" — no source spec at docs/specs/%s/spec.md'
                                   % (rel(root, doc.path), t, req.name, cap)))
            elif req.name not in names:
                violations.append((3, 'CHECK 3: %s: %s requirement "%s" not found in docs/specs/%s/spec.md'
                                   % (rel(root, doc.path), t, req.name, cap)))


def check4(deltas, root, violations):
    for doc in deltas.values():
        for req in doc.requirements:
            if len(req.types) != 1 or req.types[0] not in ("ADDED", "MODIFIED"):
                continue                       # REMOVED needs no scenarios
            if not req.scenarios:
                violations.append((4, 'CHECK 4: %s: %s requirement "%s" (line %d) has no #### Scenario'
                                   % (rel(root, doc.path), req.types[0], req.name, req.line)))
                continue
            for scen in req.scenarios:
                missing = [kw for kw, rx in (("GIVEN", RE_GIVEN), ("WHEN", RE_WHEN), ("THEN", RE_THEN))
                           if not any(rx.match(l) for l in scen.body)]
                if missing:
                    violations.append((4, 'CHECK 4: %s: requirement "%s" scenario "%s" (line %d) missing %s'
                                       % (rel(root, doc.path), req.name, scen.name, scen.line, ", ".join(missing))))


def _iter_links(change_dir, root, violations):
    """Yield (mdfile, target) for every markdown link in the change's *.md files."""
    for md in sorted(change_dir.rglob("*.md")):
        text = read_text_safe(md, root, violations)
        if text is None:
            continue
        for target in RE_MDLINK.findall(text):
            yield md, target.strip()


def link_is_broken(md, target):
    """True if `target` is a relative link from `md` that doesn't resolve on disk.
    External schemes, in-page anchors and empty targets are not links to a file."""
    if not target or target.startswith("#") or RE_SKIP_LINK.match(target):
        return False
    pathpart = target.split("#", 1)[0]
    if not pathpart:
        return False                           # in-page anchor
    return not (md.parent / pathpart).resolve().exists()


def check5(change_dir, root, violations, seen=None):
    """Broken relative links inside ONE change. `seen` collects the files scanned so the
    tree-wide sweep (check 8) doesn't report the same link twice."""
    for md, target in _iter_links(change_dir, root, violations):
        if seen is not None:
            seen.add(md)
        if link_is_broken(md, target):
            violations.append((5, "CHECK 5: %s: broken relative link -> %s" % (rel(root, md), target)))


def check6(change_dir, root, violations):
    tasks = change_dir / "tasks.md"
    if not tasks.exists():
        return                                 # check 1 reports the absence
    text = read_text_safe(tasks, root, violations)
    if text is None:
        return
    lines = [i for i, l in enumerate(text.splitlines(), start=1) if RE_UNCHECKED.match(l)]
    if lines:
        violations.append((6, "CHECK 6: %s: %d unchecked task(s) remain (lines: %s)"
                           % (rel(root, tasks), len(lines), ", ".join(map(str, lines)))))


def check7(change_dir, root, violations):
    adr_dir = root / "docs" / "adr"
    for md, target in _iter_links(change_dir, root, violations):
        if not target or RE_SKIP_LINK.match(target):
            continue
        pathpart = target.split("#", 1)[0]
        m = RE_ADR.search(pathpart)
        if not m:
            continue
        if (md.parent / pathpart).resolve().exists():
            continue
        if (adr_dir / m.group(1)).exists():     # fallback: a bare NNNN-*.md name under docs/adr/
            continue
        violations.append((7, "CHECK 7: %s: referenced ADR not found -> %s" % (rel(root, md), target)))


def check8(root, violations, findings, skip):
    """Tree-wide relative-link sweep over docs/**/*.md. Returns the number of files scanned.

    Check 5 is change-scoped, and resolve_targets() excludes archive/ by name, so the moment
    spec-archive moves a change one level deeper into docs/changes/archive/ the per-change
    check goes blind to exactly the links that move just broke: the moved change's own
    outbound links (now one ../ short) and every inbound link from docs/adr/, docs/specs/, or
    a previously-archived change. Walking the whole tree is the only form of this check that
    still works when a change is archived, renamed, or moved by hand.

    Findings land in `findings`, not `violations` — the caller decides whether they gate
    (--strict-links) or merely warn. Read errors are real violations and still go to
    `violations`. Files already scanned by check 5 are skipped so nothing is reported twice.
    """
    docs = root / "docs"
    if not docs.is_dir():
        return 0
    scanned = 0
    for md in sorted(docs.rglob("*.md")):
        if md in skip:
            continue
        scanned += 1
        text = read_text_safe(md, root, violations)
        if text is None:
            continue
        for target in RE_MDLINK.findall(text):
            target = target.strip()
            if link_is_broken(md, target):
                findings.append((8, "CHECK 8: %s: broken relative link -> %s" % (rel(root, md), target)))
    return scanned


def resolve_targets(changes_dir, change_id, root, violations):
    if change_id:
        d = changes_dir / change_id
        if not d.is_dir():
            violations.append((1, "CHECK 1: %s: change directory not found" % rel(root, d)))
            return []
        return [d]
    return [d for d in sorted(changes_dir.iterdir()) if d.is_dir() and d.name != "archive"]


# --- status mode (informational; always exits 0) ----------------------------
def requirement_wellformed(req):
    """Intrinsic structural well-formedness of one delta requirement (no source cross-ref):
    exactly one **Type:**; ADDED/MODIFIED need >=1 scenario, each with GIVEN + WHEN + THEN;
    REMOVED needs none. This is the per-requirement notion the status readout maps onto."""
    if len(req.types) != 1:
        return False
    if req.types[0] == "REMOVED":
        return True
    if not req.scenarios:
        return False
    for scen in req.scenarios:
        if not (any(RE_GIVEN.match(l) for l in scen.body)
                and any(RE_WHEN.match(l) for l in scen.body)
                and any(RE_THEN.match(l) for l in scen.body)):
            return False
    return True


def artifact_states(change_dir):
    """Map the four planning artifacts onto (name, state, needs, optional) tuples per the chain
    proposal -> delta-specs -> design[optional] -> tasks. State is done | ready | blocked,
    computed from presence + the well-formedness the validator already knows how to compute."""
    sink = []   # status never emits violations; swallow any read issues into a throwaway list

    proposal_done = (change_dir / "proposal.md").exists()

    deltas = parse_deltas(change_dir, change_dir, sink)
    delta_done = any(any(requirement_wellformed(r) for r in doc.requirements)
                     for doc in deltas.values())

    design_done = (change_dir / "design.md").exists()

    tasks = change_dir / "tasks.md"
    tasks_done = False
    if tasks.exists():
        txt = read_text_safe(tasks, change_dir, sink)
        if txt is not None:
            tasks_done = any(RE_TASK.match(l) for l in txt.splitlines())

    def state(done, prereq_ok, prereq_name):
        if done:
            return ("done", None)
        if not prereq_ok:
            return ("blocked", prereq_name)
        return ("ready", None)

    rows = []
    rows.append(("proposal", "done" if proposal_done else "ready", None, False))
    ds, dsn = state(delta_done, proposal_done, "proposal")
    rows.append(("delta-specs", ds, dsn, False))
    de, den = state(design_done, proposal_done, "proposal")
    rows.append(("design", de, den, True))
    ts, tsn = state(tasks_done, delta_done, "delta-specs")
    rows.append(("tasks", ts, tsn, False))
    return rows


def render_change(change_id, rows):
    """Render one change's chain readout as lines. ✓ done, ◆ actionable-next, ○ optional/blocked."""
    lines = [change_id]
    width = max(len(name) for name, *_ in rows)
    for name, st, needs, optional in rows:
        if st == "done":
            sym = "✓"                       # ✓
        elif st == "ready" and not optional:
            sym = "◆"                        # ◆ the next thing to create
        else:
            sym = "○"                        # ○ optional-ready or blocked
        if st == "ready" and optional:
            label = "ready (optional)"
        elif st == "blocked" and needs:
            label = "blocked — needs: %s" % needs
        else:
            label = st
        lines.append("  %s %s  %s" % (sym, name.ljust(width), label))
    return lines


def status_mode(changes_dir, change_id):
    """Print the presence-based chain readout; always return 0."""
    if not changes_dir.exists():
        print("(no docs/changes/ in this repo — nothing to report)")
        return 0
    if change_id:
        d = changes_dir / change_id
        if not d.is_dir():
            print("%s\n  (change directory not found under docs/changes/)" % change_id)
            return 0
        targets = [d]
    else:
        targets = [d for d in sorted(changes_dir.iterdir()) if d.is_dir() and d.name != "archive"]
        if not targets:
            print("(no active changes under docs/changes/)")
            return 0
    blocks = ["\n".join(render_change(d.name, artifact_states(d))) for d in targets]
    print("\n\n".join(blocks))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Deterministic structural validator for spec-workflow changes.")
    ap.add_argument("mode", nargs="?", choices=["status"], default=None,
                    help="'status': print the artifact-chain readout for a change (informational; always exits 0)")
    ap.add_argument("--change", help="validate only docs/changes/<ID>/")
    ap.add_argument("--all", action="store_true",
                    help="validate all active (non-archived) changes (the default when --change is omitted)")
    ap.add_argument("--archive", action="store_true",
                    help="also enforce check 6 (no unchecked tasks); used by spec-archive")
    ap.add_argument("--strict-links", action="store_true",
                    help="promote check 8 (tree-wide broken relative links under docs/) from "
                         "warnings to violations; used by spec-archive after the move")
    ap.add_argument("--project-dir", help="repo root (else $CLAUDE_PROJECT_DIR, git toplevel, or CWD)")
    a = ap.parse_args()

    root = project_dir(a.project_dir)
    changes_dir = root / "docs" / "changes"

    if a.mode == "status":
        return status_mode(changes_dir, a.change)

    if not changes_dir.exists():
        return 0                               # nothing to validate; safe no-op across non-spec repos

    specs_dir = root / "docs" / "specs"
    violations = []
    cache = {}
    scanned_md = set()

    for ch in resolve_targets(changes_dir, a.change, root, violations):
        check1(ch, root, violations)
        deltas = parse_deltas(ch, root, violations)
        check2(deltas, root, violations)
        check3(deltas, specs_dir, cache, root, violations)
        check4(deltas, root, violations)
        check5(ch, root, violations, scanned_md)
        check7(ch, root, violations)
        if a.archive:
            check6(ch, root, violations)

    link_findings = []
    swept = check8(root, violations, link_findings, scanned_md)
    # The count is the guard: "0 broken" means nothing when 0 files were scanned.
    print("link sweep: %d file(s) scanned under docs/, %d broken relative link(s)%s"
          % (swept + len(scanned_md), len(link_findings),
             "" if a.strict_links else " (warnings; --strict-links to gate on them)"))
    if a.strict_links:
        violations.extend(link_findings)
    elif link_findings:
        print("\n".join("WARN " + msg for _, msg in link_findings), file=sys.stderr)

    if violations:
        out = []
        for n in sorted(set(v[0] for v in violations)):     # group by check, keep discovery order within
            out.extend(msg for vn, msg in violations if vn == n)
        print("\n".join(out), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
