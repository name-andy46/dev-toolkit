#!/usr/bin/env bash
#
# Scan the repo for credentials and environment-specific identifiers that must
# never reach a public marketplace.
#
# The patterns tracked here are deliberately GENERIC — naming your own private
# hosts, accounts, or companies in this file would itself leak them. Keep the
# specifics in an untracked local denylist instead:
#
#   .scan-local            one "label|regex" per line, '#' comments allowed
#
# (.scan-local is gitignored. Override the path with SCAN_LOCAL=/some/file.)
#
# Usage: scripts/scan.sh [path ...]      (defaults to the repo root)
# Exit:  0 clean, 1 something matched.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="scan.sh"
SCAN_LOCAL="${SCAN_LOCAL:-$ROOT/.scan-local}"
TARGETS=("$@")
[[ ${#TARGETS[@]} -eq 0 ]] && TARGETS=("$ROOT")

# What to scan: for a whole-repo run, ask git for the files that would actually be
# published — tracked plus untracked-but-not-ignored, exactly what `git add -A`
# would stage. Gitignored files (a local dev container, .scan-local, .env) cannot
# leak, and flagging them every run would train you to ignore the scanner.
# An explicit path argument is always scanned as given, git or not.
SCAN_ARGS=("${TARGETS[@]}")
if [[ ${#TARGETS[@]} -eq 1 && "${TARGETS[0]}" == "$ROOT" ]] \
   && git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  SCAN_ARGS=()
  while IFS= read -r -d '' f; do SCAN_ARGS+=("$ROOT/$f"); done \
    < <(git -C "$ROOT" ls-files -co --exclude-standard -z)
  if [[ ${#SCAN_ARGS[@]} -eq 0 ]]; then
    echo "nothing to scan — no tracked or unignored files"
    exit 0
  fi
  echo "Scanning ${#SCAN_ARGS[@]} committable file(s)"
fi

# label|extended-regex
PATTERNS=(
  'AWS access key id|\b(AKIA|ASIA)[0-9A-Z]{16}\b'
  'AWS secret key assignment|aws_secret_access_key[[:space:]]*[=:][[:space:]]*[A-Za-z0-9/+=]{20,}'
  'AWS account id (12 digits)|\b[0-9]{12}\b'
  'Private key block|-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'Slack token|xox[baprs]-[0-9A-Za-z-]{10,}'
  'Slack webhook url|hooks\.slack\.com/services/'
  'Atlassian/Bitbucket token|\bAT[CB]TT[0-9A-Za-z_=+/-]{10,}'
  'GitHub token|\bgh[pousr]_[0-9A-Za-z]{20,}'
  'Generic bearer/api key assignment|(api[_-]?key|auth[_-]?token|password|passwd|secret)[[:space:]]*[=:][[:space:]]*["'"'"']?[A-Za-z0-9_/+=-]{16,}'
  'Private IPv4 address|\b(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)[0-9]{1,3}\.[0-9]{1,3}\b'
  'Public IPv4 address|\b([0-9]{1,3}\.){3}[0-9]{1,3}\b'
  'Atlassian site hostname|[a-z0-9][a-z0-9-]*\.atlassian\.net'
  'Internal AWS hostname|(\.compute\.internal|\.rds\.amazonaws\.com|\.cache\.amazonaws\.com|\.elb\.amazonaws\.com|\.execute-api\.[a-z0-9-]+\.amazonaws\.com|ec2-[0-9-]+\.[a-z0-9-]+\.compute\.amazonaws\.com)'
  'Author-specific home path|/(home|Users)/[A-Za-z0-9._-]+/'
)

# Per-label allow-list: a matched LINE is dropped if it also matches this regex.
# Used where a broad pattern is the only practical one — a bare dotted quad can't
# be narrowed structurally in POSIX ERE (no lookahead), so instead we subtract the
# addresses that are legitimate in documentation: loopback, link-local (including
# the EC2 metadata endpoint), broadcast, the RFC 5737 documentation ranges, and the
# private ranges already reported under their own label.
# Caveat: this drops the whole line, so a real address sharing a line with an
# allowed one is missed. Keep example addresses on their own line.
declare -A ALLOW=(
  ['Public IPv4 address']='\b(0|127)\.|\b169\.254\.|\b10\.|\b192\.168\.|\b172\.(1[6-9]|2[0-9]|3[01])\.|\b(192\.0\.2|198\.51\.100|203\.0\.113)\.|255\.255\.255\.255'
)

if [[ -f "$SCAN_LOCAL" ]]; then
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    PATTERNS+=("$line")
  done < "$SCAN_LOCAL"
  echo "Loaded extra patterns from $SCAN_LOCAL"
fi

hits=0
for entry in "${PATTERNS[@]}"; do
  label="${entry%%|*}"
  regex="${entry#*|}"
  # -i: patterns are POSIX ERE (no inline (?i) flag), so match case-insensitively
  # everywhere rather than making every pattern spell out character classes.
  matches="$(grep -rIinE --binary-files=without-match \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ \
    --exclude="$SELF" --exclude=".scan-local" \
    -e "$regex" "${SCAN_ARGS[@]}" 2>/dev/null)" || true
  if [[ -n "$matches" && -n "${ALLOW[$label]:-}" ]]; then
    matches="$(printf '%s\n' "$matches" | grep -vE "${ALLOW[$label]}")" || true
  fi
  if [[ -n "$matches" ]]; then
    hits=$((hits + 1))
    printf '\n\033[31m✘ %s\033[0m\n' "$label"
    printf '%s\n' "$matches" | sed 's|^'"$ROOT"'/||' | sed 's/^/    /'
  fi
done

if [[ $hits -gt 0 ]]; then
  printf '\n\033[31m%d pattern(s) matched — review every line above before committing.\033[0m\n' "$hits"
  echo "False positive? Narrow the pattern in scripts/scan.sh, don't delete the check."
  exit 1
fi

printf '\033[32m✔ scan clean\033[0m\n'
