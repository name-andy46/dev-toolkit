# check-my-analysis — the check catalogue

What to check, how to detect it, and what the fix looks like. Work the stages in order; a fault in
an earlier stage makes later stages meaningless.

Nothing here is vendor-specific except the clearly marked `yfinance` section. **Verify library
behaviour at runtime rather than trusting a remembered default** — these libraries change defaults
between versions, and the version installed is the only one that matters.

---

## Stage 1 — Data hygiene

### 1.1 Adjustment: is the series adjusted, and consistently?

**What goes wrong.** Split- and dividend-adjusted closes combined with raw `High`/`Low`/`Open`. A
2:1 split then reads as a −50% crash on the unadjusted columns while the close is smooth, so every
range-based indicator (ATR, Bollinger width, Donchian, anything using the high or low) is wrong
across the split date. The series still looks plausible on a chart.

**Detect.** Check for `Low > Close` or `High < Close` on any bar — both impossible within a single
bar. `Low > Close` is the usual fingerprint: adjustment scales older closes *down*, so an adjusted
close sitting below a raw low is exactly what a split leaves behind. Then look for single-bar moves
near a round ratio (2:1, 3:1, 10:1) and check whether a corporate action falls on that date.

**Fix.** Use one convention for every column. If adjusted, all of OHLC adjusted; if raw, all raw
and no cross-split lookbacks.

### 1.2 Gaps, halts and holidays

**What goes wrong.** A forward-fill turns a non-trading day into a flat candle with zero range,
which drags ATR down and can satisfy a "low volatility" filter with a day the market was shut. A
`dropna()` earlier in the pipeline silently shortens the series instead of raising.

**Detect.** Count bars per ticker over the same date range and compare against the exchange
calendar (or against the modal bar count across the universe). Count bars where
`High == Low == Close` — legitimate but rare, common in fabricated rows.

**Fix.** Leave non-trading days absent rather than filled. If a ticker is genuinely missing
sessions, exclude it and report how many were dropped.

### 1.3 Enough history for the longest lookback

**What goes wrong.** A 200-day moving average on a ticker with 150 bars returns a number for the
bars where the window is short, or `NaN`, depending on `min_periods` — and either way it isn't a
200-day average. Recent IPOs are the usual culprit.

**Detect.** For the longest lookback *N*, count tickers with fewer than *N* + a margin of bars.
Check whether `min_periods` is set on any `rolling()` call.

**Fix.** Require `N` bars of history to enter the universe, and report how many symbols that
excludes.

### 1.4 Timezone and session labelling

**What goes wrong.** A daily bar stamped in UTC can belong to the previous exchange session, so
every signal is one day out of step with what the trader sees on their platform. Mixed tz-aware
and tz-naive indexes also silently misalign on join.

**Detect.** Print `df.index.tz` and the last few index values, and reconcile the final bar's date
against the exchange's last session. If several sources are joined, check every index's tz.

**Fix.** Normalise every series to the exchange's local session date before joining or comparing.

### 1.5 Silent fetch failures

**What goes wrong.** A mistyped or delisted symbol returns an empty frame rather than an error;
rate limiting returns partial history. Downstream code treats "no data" as "no signal" and the
ticker vanishes from the screen without anyone noticing.

**Detect.** Assert a row count per symbol immediately after fetch. Compare the requested symbol
list against what actually came back, and report the difference.

**Fix.** Fail loudly per symbol, retry on partial data, and report the symbols that never arrived.

---

## Stage 2 — Indicator correctness

### 2.1 The current bar is incomplete (the big one for screening)

**What goes wrong.** A screen run at 11:00 gets a daily bar still forming: its "close" is the last
trade, its high and low are partial. Every indicator built on it changes through the session, so
the screen isn't reproducible an hour later and can't be compared with yesterday's run. This is the
single most common reason two runs of the same screen disagree.

**Detect.** Compare the last bar's date against the last *completed* session. Run the screen twice
an hour apart, or drop the last bar and re-run — if the result set moves, it depends on a partial
bar.

**Fix.** A judgment call for the user, not for you: use the last completed bar (reproducible,
one day behind) or accept an intraday bar (current, not reproducible). Present both, with that
consequence, and let them choose.

### 2.2 Warmup NaNs

**What goes wrong.** The first *N*−1 bars of an *N*-period indicator are `NaN`. Whether a `NaN`
counts as failing a filter or as excluding the symbol changes the universe size — and the two are
easy to confuse, since `NaN > threshold` is `False`, which reads as "failed the filter" rather than
"unknown".

**Detect.** Count `NaN`s in each indicator column at the bar being screened. Report the universe
size both ways: NaN-as-fail and NaN-excluded.

**Fix.** Decide explicitly and state it in the output. Usually: exclude the symbol and report the
count, rather than letting it silently fail a filter it was never evaluated against.

### 2.3 Rolling-window off-by-one

**What goes wrong.** `rolling(20).mean()` at bar *t* includes bar *t*, so it is only knowable once
*t* has closed. Using it to make a decision *during* bar *t* uses information from the future.

**Detect.** For one ticker, recompute the indicator by hand for a specific bar and compare. Check
whether any signal is compared against the same bar's close without a shift.

**Fix.** Shift the signal by one bar, or state clearly that the decision happens at the close of
the same bar. Then re-run and report how the result set changed.

### 2.4 Repainting

**What goes wrong.** Centred windows (`center=True`), and indicators like ZigZag or anything
smoothing symmetrically, revise their own history. Backwards they look prescient; forwards they
don't exist yet.

**Detect.** Compute the indicator on data up to bar *t*, then on the full series, and compare the
value at *t*. Any difference means it repaints.

**Fix.** Use a trailing window only.

### 2.5 Chained or duplicated smoothing

**What goes wrong.** An indicator applied to an already-smoothed series (an EMA of an EMA that was
meant to be an EMA of price) lags far more than the parameter suggests, so the trader's mental model
of "20-day" is wrong.

**Detect.** Trace the input of each indicator back to raw price. Compare the indicator's lag against
a fresh calculation from price.

**Fix.** Compute from price unless double smoothing is intended.

---

## Stage 3 — Screener construction

### 3.1 Cross-sectional staleness

**What goes wrong.** Ranking 500 tickers where a handful have a last bar from days ago — halted,
delisted, thinly traded, or a different exchange calendar. Those are being compared against today's
prices for everyone else, and stale names often rank oddly high or low.

**Detect.** Group the universe by last-bar date and print the distribution. Anything not on the
most recent session is suspect.

**Fix.** Require the last bar to be the current session (or the last completed one), and report how
many symbols that drops.

### 3.2 Where the universe comes from

**What goes wrong.** A hardcoded ticker list goes stale as symbols are renamed, merged or delisted.
For screening today's market this mostly shows up as silent fetch failures (1.5) rather than
survivorship bias — but a list that quietly shrinks changes what the screen can find.

**Detect.** Count the symbols in the list against the symbols with usable data. Check for a
hardcoded list with no date on it.

**Fix.** Report the shrinkage on every run, so a decaying list is visible rather than invisible.

### 3.3 Liquidity and price floors

**What goes wrong.** With no floors, a screen's extremes fill with illiquid and very low-priced
names, where a one-tick move is a large percentage and indicators are dominated by noise. The list
looks full of opportunities and is untradeable.

**Detect.** Report median dollar volume and price for the screen's output versus the universe. If
the output skews far lower on either, the screen is finding illiquidity, not signal.

**Fix.** Suggest that a floor is *missing* — a factual gap in the filter set. Do not pick the
threshold for them; that's a strategy decision.

### 3.4 Ranking mechanics

**What goes wrong.** Ties broken by whatever order the data arrived in, so the "top 10" changes
between runs with identical inputs. `sort_values()` with `NaN`s present places them in a way that
depends on `na_position`. Percentile ranks over a universe that changed size between runs aren't
comparable.

**Detect.** Run twice on identical cached input and diff the ordering. Count `NaN`s in the ranking
column and check where they land.

**Fix.** An explicit deterministic tiebreak, and NaNs excluded before ranking rather than sorted.

### 3.5 Filter combination

**What goes wrong.** Conditions combined with `and` instead of `&` on Series, which raises "the
truth value of a Series is ambiguous" — note that `and` *is* correct once single values have been
extracted with `.iloc[-1]`, which is why the mistake survives a read-through. Also: missing
parentheses around chained comparisons, and a filter applied to the whole history rather than the
screening bar, which passes a ticker that met the condition once, years ago.

**Detect.** For 2–3 tickers that passed, verify each condition individually at the screening bar.
For 2–3 that failed, verify which condition rejected them. A filter that rejects nothing or
everything is the giveaway.

**Fix.** Evaluate every condition at the single screening bar, and report per-condition pass counts
so a filter doing nothing is visible.

---

## `yfinance` specifics

Confirmed in use, so check these explicitly. **Do not assume a default** — read the installed
version and inspect the object you actually got back.

- **Adjustment default has changed between versions.** Don't reason about `auto_adjust` from
  memory; check the version and whether an `Adj Close` column is present alongside `Close`. Cross-
  check with 1.1 (`High < Close`).
- **Column shape varies.** `download()` can return a MultiIndex (`(field, ticker)`) — including for
  a single ticker in some versions — while `Ticker.history()` returns flat columns. Code written
  against one shape breaks silently against the other, often producing a column of `NaN`.
  Inspect `df.columns` rather than assuming.
- **A bad symbol yields an empty frame, not an exception**, sometimes with a message printed to
  stdout that no `try/except` will catch. See 1.5.
- **Rate limiting returns partial or empty history** rather than failing. Re-fetching a symbol that
  came back short is how you tell.
- **Index timezone differs** between daily and intraday, and across versions. See 1.4.
- **`actions=True`** gives dividends and splits, which is the cheap way to confirm whether a jump
  found in 1.1 is a corporate action.
- **Bulk downloads partially fail.** Compare the requested list against the columns present.

---

## Not in scope

Backtest mechanics — slippage, commissions, fill assumptions, position sizing, out-of-sample
splitting — are deliberately absent: this catalogue is for screening and current-market analysis.
If the user is backtesting, say that this skill doesn't cover the backtest-specific faults (of
which lookahead bias in the fill is the most damaging) rather than auditing it half-way.

And nothing here evaluates a strategy. Report computation faults; leave thresholds, parameters and
whether the idea is any good to the user.
