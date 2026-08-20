# market-analysis

Checks for people who use Python to analyse markets but don't read Python.

If you know your domain and let Claude write the code, you can usually tell when a *result* is
wrong — a screen returning 340 tickers, a name that hasn't traded in a week, two runs of the same
screen disagreeing. What you can't see is the line that caused it. This plugin closes that gap: it
audits the code and the data behind a result and explains what it found in terms of the result, not
the code.

## Skills

### check-my-analysis

Audits technical-analysis and stock-screening code for the faults that make output look cleaner or
better than reality, in three stages — **data hygiene**, then **indicator correctness**, then
**screener construction**. It reports findings with evidence first and applies fixes only once you
confirm them.

Some of what it looks for:

- **Mixed adjustment** — split-adjusted closes combined with raw highs and lows, so every
  range-based indicator (ATR, Bollinger width, Donchian) is wrong across a split date.
- **An incomplete current bar** — a screen run mid-session builds indicators on a bar that's still
  forming, which is the most common reason the same screen gives different answers an hour apart.
- **Cross-sectional staleness** — ranking a universe where some symbols' last bar is days old, so
  they're being compared against everyone else's current prices.
- **Warmup NaNs counted as filter failures** — a 200-day average has no value for a symbol's first
  199 bars, and `NaN > threshold` is `False`, which silently reads as "failed" rather than "unknown".
- **Silent fetch failures** — a mistyped or delisted symbol returns an empty frame instead of an
  error, and quietly leaves your universe.
- **Rolling-window off-by-one and repainting** — indicators that need a bar to close before they're
  knowable, or that revise their own history.

`yfinance` gets its own set of checks, since its defaults and column shapes have changed between
versions in ways that fail silently rather than loudly.

**Triggers:** "check my analysis", "check my screener", "audit my indicator", "my results look
off", "why does my screen return these", "why did my screen change", "verify this data", "did I get
the bars right".

**What it will not do:** assess whether a strategy is good. It verifies that the computation is
honest — no edge claims, no parameter suggestions, no view on whether a result will persist. A
clean audit means the arithmetic is sound and nothing more.

**Not covered:** backtest mechanics (slippage, fills, position sizing, out-of-sample splitting).
The checks target screening and current-market analysis. If you're backtesting, the skill says so
rather than auditing half the problem.

## Configuration

None. The checks are source-agnostic, with `yfinance`-specific rules applied when that's what the
code uses, and the skill inspects your actual data and library versions at runtime rather than
assuming defaults.
