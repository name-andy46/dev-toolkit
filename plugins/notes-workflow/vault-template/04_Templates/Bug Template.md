---
type: bug
ticket:            # REQUIRED — a bug is a tracked defect. No ticket yet? use the Investigation template instead.
status: investigating   # investigating → root-caused → fixing → merged → verifying-prod → resolved (off-ramp: wontfix)
refs: []           # optional: device / org / alarm / commit ids
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [bug]
---
# Bug — <Title>

**Ticket:** <SLC-XXXXX>
**Related:** <[[other-note]] — how it relates>

## Symptom
<observed behavior>

## Impact
<who/what is affected; scope>

## Timeline
- YYYY-MM-DD:

## Findings
<evidence chain — what the diagnosis turned up>

## Root Cause
<confirmed cause, with file:line>

## Fix / Resolution
<the fix. As it progresses, record: commit/branch (status `fixing`) → merged to develop (`merged`)
→ deployed (`verifying-prod`) → verified in production (`resolved`). Note the regression test.>

**Remaining before `resolved`:**
- [ ] <PR / merge / deploy / verify steps still outstanding>

## Open Questions
-

## References
- <code paths, logs, dashboards, commits>
