---
name: check-my-analysis
description: >-
  Audits Python technical-analysis and stock-screening code for the specific faults that make
  results look cleaner or better than reality — unadjusted or mixed price series, gaps and stale
  bars, an incomplete current session bar, indicator warmup NaNs, rolling-window off-by-one,
  repainting, and screener construction faults like NaN-as-fail, missing liquidity floors, and
  cross-sectional staleness. Use whenever the user wants their market analysis, screener,
  indicator, or price data checked, verified, reviewed, audited or debugged, and whenever a result
  looks surprising — a screen returns an odd list, two runs of the same screen disagree, a number
  doesn't reconcile, or an indicator looks too good. Triggers on "check my analysis", "check my
  screener", "is this right", "why does my screen return these", "audit my indicator", "my results
  look off", "verify this data", "did I get the bars right", "why did my screen change". Reports
  findings in results terms with evidence and offers fixes on confirmation. It checks whether the
  computation is sound — never whether a strategy is good.
---

# check-my-analysis

Audit market-analysis code the user cannot audit themselves.

The person running this usually knows their domain well and does not read Python. They can tell
you a result smells wrong — "no screen should return 340 tickers", "that stock hasn't traded in a
week" — but they cannot see the missing `.shift(1)` or the `Adj Close` mixed with a raw `High`.
Your job is to find the fault, prove it in terms of the *result*, and fix it only once they say so.

**The bundled `CHECKLIST.md` beside this file is the catalogue of what to check and how to test
each one.** Read it before you start; don't work from memory.

## The boundary (non-negotiable)

You check whether the **computation is sound**. You never assess whether a **strategy is good**.

- Do not say an approach looks profitable, promising, or sound as a strategy.
- Do not suggest parameters that would improve a result.
- Do not comment on whether an edge is real or will persist.
- If asked, say plainly that this skill verifies computation and can't speak to strategy.

Someone may trade real money on the code you just validated. "No lookahead bias found" means the
arithmetic is honest, nothing more — say so in those words if the user starts treating a clean
audit as an endorsement.

## Stage 0 — Find out what you're auditing

Before checking anything, establish and state back:

1. **What the code is meant to produce** — a screen of tickers, one indicator, a ranking, a chart.
2. **Where the bars come from** — `yfinance`, a broker API, a vendor, a saved CSV. Read the fetch
   code; don't infer from library names in imports.
3. **The universe** — how many symbols, and where the list comes from.
4. **The longest lookback** any indicator uses. This number drives several checks.
5. **When it's run** — during the session or after the close. This decides whether Stage 2's
   incomplete-bar check is a real problem or a non-issue.

If the code isn't runnable as-is, say so and ask for what's missing rather than auditing by
reading alone. Several checks in the checklist need execution.

## Stages, in order

Work the checklist in order and **stop to report when a stage produces a finding that invalidates
later stages.** Bad data makes indicator checks meaningless, and a broken indicator makes screener
checks meaningless. Don't hand over a list of thirty findings when the first one explains the rest.

1. **Data hygiene** — is the input what they think it is?
2. **Indicator correctness** — is the calculation aligned to time correctly?
3. **Screener construction** — is the universe and filter logic doing what they intend?

## Test, don't just read

Reading finds some of these; running finds the rest, and only running produces evidence the user
can judge. The checklist gives a test per item. The general shape:

- **Differential runs.** Re-run with one thing changed — the last bar dropped, signals lagged a
  bar, NaN warmup rows excluded — and diff the result set. A result that moves a lot under a
  change that *shouldn't* matter is the finding.
- **Distribution checks.** Group the universe by last-bar date, by bar count, by NaN count. The
  outliers are the bugs.
- **Reconciliation.** Recompute one ticker's indicator by hand (or with a second method) and
  compare to the code's value for the same bar.

Keep runs small. One ticker proves an alignment bug; you don't need the whole universe.

## Reporting

Findings first, each in this shape:

- **What it means for the result** — the headline, in their terms. *"14 of your 500 tickers were
  ranked on prices at least two days stale."*
- **The evidence** — the number, the diff, the ticker you checked. Never assert a fault you
  haven't demonstrated.
- **What it is** — one sentence of mechanism, in plain language, no jargon unless they used it.
- **The fix** — what you'd change, and what the result would look like afterwards.

Order by how much the result moves, not by how interesting the bug is.

If a stage is clean, say so in one line and move on. A clean audit is a real outcome and worth
stating — do not manufacture findings to look thorough.

## Fixing

**Report first. Fix only on confirmation.** They cannot review the diff, so consent replaces
review — never bundle a fix into the audit and mention it afterwards.

Then:

- **One fix at a time**, and re-run the check that found it to confirm the finding is gone.
- **Say how the result changed** after each fix, in the same terms as the finding. A fix that
  quietly changes the screen from 431 tickers to 122 is something they must be told.
- **Never adjust parameters, thresholds, or the universe to make output look better.** Fix the
  fault; leave the strategy alone. If a fix makes results dramatically worse, that's the finding,
  not a problem with the fix.
- If a fix needs a judgment call only they can make — use the last completed bar or accept an
  intraday one, treat a NaN as a fail or an exclusion — ask, with the consequence of each option.

## Related

`CHECKLIST.md` — the check catalogue, with a detection method for each item.
