# text-tools-drill — skill checklist

The **map** of what this drill covers: the Unix **pipe-filter family** — grep, sed, awk, find/xargs, and the coreutils glue. Everything is a one-liner you can attempt in *any* repo, log file, or CSV. The skill uses this ladder to calibrate difficulty (pick one notch above the learner's current comfort).

> This is the distilled map, not a textbook. Each item is a *skill to practice*, not a lesson to read. The drill teaches by posing real problems and verifying — see `SKILL.md`.

## The tools, one line each

| Tool | The question it answers | Role in a pipeline |
|------|------------------------|--------------------|
| **grep** | *Which lines match?* | **find / filter** |
| **sed** | *Change each line as it streams past.* | **transform / edit** |
| **awk** | *Treat each line as fields and compute.* | **extract / aggregate** |
| **find** (+ **xargs**) | *Which files, by name/type/age/size — and feed them onward.* | **select** (front of pipe) |
| **glue**: `sort` `uniq` `cut` `wc` `tr` | *Order, dedupe, slice, count, translate.* | **reshape / rank** (back of pipe) |

Full data flow: `find → grep/sed/awk → sort | uniq -c | sort -rn` (select → filter/transform/compute → reshape/rank). All are **Unix filters**: read stdin, write stdout, do one job, compose with `|`.

## Difficulty ladder (drill roughly in this order)

**Foundations**
- [ ] Pipes, redirection (`|`, `>`, `>>`, `2>`), exit codes (`&&`, `-q`)
- [ ] Regex basics + BRE-vs-ERE (`-E`); regex ≠ shell glob

**grep — find the lines**
- [ ] literal search + `-r` `-n`
- [ ] scope the recursion: `--include` / `--exclude-dir={venv,node_modules,.git}`
- [ ] reshape output: `-l` (files) / `-c` (count) / `-v` (invert)
- [ ] read in place: context `-A` / `-B` / `-C`
- [ ] regex matching: `-E`, anchors, char classes, alternation
- [ ] extract only the match: `-o` / `-oE`
- [ ] scripting: `-q` + exit code in a conditional

**sed — transform the stream** *(always preview before `-i`)*
- [ ] substitute: `s/old/new/` + `/g` `/I`
- [ ] select lines: `-n '10,20p'`, `-n '/start/,/end/p'`
- [ ] delete: `d` (by number and by pattern)
- [ ] groups + backrefs: `-E 's/(a)(b)/\2\1/'`
- [ ] in place, safely: `-i.bak` after a clean preview

**awk — compute on fields**
- [ ] print columns: `$1`, `$NF`
- [ ] set separator: `-F','` (CSV), `-F:` (grep output)
- [ ] filter by condition: `$3>100`, `/regex/`, `&&`/`||`
- [ ] built-ins: `NR` (line no.), `NF` (field count)
- [ ] aggregate: `{s+=$N} END{print s, s/NR}`
- [ ] **tally by key**: `count[$1]++ … END{...}` (the one to master)

**find + xargs — from one file to many**
- [ ] find by name/type: `-name '*.py'` (quote it), `-type f`
- [ ] find by metadata: `-mtime -N`, `-size +1M`, `-path`/`-not -path`, `-maxdepth`
- [ ] `xargs`: turn stdin lines into arguments (`find … | xargs grep`)
- [ ] safe feed: `find … -print0 | xargs -0 …`, or `-exec CMD {} +`

**glue + composition**
- [ ] rank anything: `sort | uniq -c | sort -rn` (`uniq` needs a prior `sort`)
- [ ] `cut -d',' -f2`, `wc -l`, `tr A-Z a-z`
- [ ] full pipeline end to end: `find | xargs grep | awk | sort | uniq -c | sort -rn`
- [ ] safe mass find-and-replace: `grep -rl OLD .` → `xargs sed -i.bak 's/OLD/NEW/g'` → verify zero remain

## Common traps to check in verification
- Unscoped `grep -r` drowning in `venv/` / `node_modules/`.
- Confusing a shell glob (`*.py`) with a regex (`*` = zero-or-more).
- BRE needing `\(`, `\|`, `\+` — reach for `-E` instead.
- `sed -i` with no preview (no undo).
- `find … | grep X` (searches the filename list) vs `find … | xargs grep X` (searches contents).
- `uniq` without a preceding `sort` (only collapses *adjacent* duplicates).

