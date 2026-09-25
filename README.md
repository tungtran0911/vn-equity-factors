# HOSE Equities: Trend, Short-Term Reversal and the Daily Price Limit

This study sorts HOSE stocks on their past returns at three horizons -- twelve
months, one month and one week -- and asks which horizons carry information about
future returns, and whether any of it survives the costs of a long-only investor,
the only kind the market permits.

Twelve-month momentum carries none: the winner-minus-loser spread is -0.07% a month
(t = -0.15) over 113 months. One-month returns do not reverse as they do in
developed markets; they continue. Last month's losers trail the equal-weighted
universe by 0.50% a month (t = -2.77), while last month's winners are barely above
it. At a one-week horizon, entered one session after formation, there is nothing
(+0.07% a week, t = +0.75). After a 0.4% round-trip cost no long-only quintile beats
the universe at any of the three horizons.

The short-horizon structure that does exist lives in a single session and is
organised by the +/-7% daily price limit. A stock that closes at or near its ceiling
outperforms the universe by 1.69% the next session (t = 39); a stock that rises 3%
to 6.5% underperforms by 0.39% (t = -23). Large moves inside the band reverse; moves
the band truncates continue. The continuation cannot be traded at the close -- a
stock locked at its limit has no counterparty at that price -- which is why a
strategy that enters one session late finds none of it.

This is the first of three factor families. Liquidity (turnover, size, spread) and
volatility (idiosyncratic volatility, beta) follow; section 8 lists what each needs.

---

## 1. Market structure

| | |
|---|---|
| Exchange | Ho Chi Minh Stock Exchange (HOSE), about 400 listed stocks |
| Daily price limit | +/-7% of the reference price (the previous close) |
| Short selling | not permitted; a long-short spread is not a position anyone can hold |
| Trading cost assumed | 0.4% round trip: brokerage of about 0.15% per side plus 0.1% personal income tax on sales. Brokerage varies by broker, so results are also shown at 0.2% and 0.6% |

The price limit shapes everything below. When the price that clears supply and
demand lies outside the band, the stock closes at the limit with unfilled orders on
one side, and that imbalance carries into the next session.

## 2. Data

**Source.** Daily bars for every stock currently listed on HOSE, from KBS's public
endpoints, called directly: 887,291 bars for 404 of 405 stocks (one, SBV, failed to
download), 2016-01-04 to 2026-09-25.

**Adjustment.** Prices are adjusted by the provider for corporate actions. The
evidence is in the data: Vietnamese companies pay stock dividends often, and an
unadjusted stock dividend of 8% or more would show as a move beyond the 7% band.
Within each stock's HOSE history only 148 such moves remain in more than 800,000
bars. The adjustment method is undocumented, and so is whether volume is restated to
match the prices. Adjusted price times volume is therefore not treated as traded
value: no filter or weight in this study uses it.

**Cross-check.** Against a second provider (VCI) over 767,923 overlapping
stock-days, daily returns differ by more than 0.5% on 0.156% of days and by more than
2% on 0.046%.

**HOSE history only.** About a quarter of today's HOSE stocks traded on UPCoM
(+/-15% band) or HNX (+/-10%) before transferring. Each stock enters the panel the
day after its HOSE listing date, taken from the provider's company profile; the
listing day itself is dropped, since its return is measured against another
exchange's price. This removes 63,484 bars. Daily moves larger than 7.5% -- which
cannot happen on HOSE between consecutive sessions -- fall from 3,989 to 148. Any
signal window containing one of the remaining 148 is excluded.

**Coverage.** Stocks with HOSE-era data: 254 in 2016, 308 in 2018, 338 in 2020, 365
in 2022, 378 in 2024, 403 in 2026.

**Survivorship.** The universe is today's listing. Stocks that were delisted between
2016 and 2026 are absent. Delisted stocks are disproportionately past losers, so this
bias raises the measured return of loser portfolios; the loser underperformance in
section 4.2 is, if anything, understated.

**Eligibility.** At each formation date a stock enters the sort only if, over the
signal window plus the preceding 60 sessions, it was HOSE-listed, traded on at least
95% of market days, and never moved beyond the band between consecutive sessions.
The provider omits days without trades rather than recording zero volume, so
tradability is measured against the market calendar. On average 255 to 268 stocks
are eligible per formation date.

## 3. Method

**Signals.**

- Momentum 12-1: return from month-end t-12 to month-end t-1. The most recent month
  is skipped because it behaves differently (section 4.2); including it would net two
  effects into one number.
- One-month: return over the last calendar month.
- One-week: return over the last week.

**Portfolios.** Eligible stocks are ranked and split into equal-weighted quintiles,
Q1 holding the lowest past return. Positions are entered at the close one session
after formation and held to the close one session after the next formation date.
Without that skip, the signal and the entry would share a closing price, and any
move in the following session -- including the price-limit spillover of section 4.4
-- would be credited to a strategy that could not have traded it.

**Long leg, short leg.** The long leg is the quintile the strategy's premise says to
buy: Q5 for momentum, Q1 for the reversal signals. The long-short spread is reported
as a description of the cross-section. The implementable quantity is the long leg's
return over the equal-weighted universe, after costs.

**Costs.** Turnover is the share of a quintile's names that are new at each
rebalance (equal weights, drift ignored). Each rebalance costs turnover times the
round-trip cost, charged to the long leg.

**Inference.** Newey-West t-statistics with lag length floor(4 (T/100)^(2/9)).
Holding periods do not overlap, but consecutive returns are not independent.

## 4. Results

Mean returns per holding period, equal-weighted, in percent.

### 4.1 Twelve-month momentum: nothing

Monthly, 2017-03 to 2026-07, 113 months.

| | Q1 (losers) | Q2 | Q3 | Q4 | Q5 (winners) | Universe |
|---|---|---|---|---|---|---|
| Return per month | +1.23 | +1.38 | +1.35 | +1.33 | +1.16 | +1.29 |
| Turnover per month | 27% | 52% | 55% | 49% | 24% | |

Winners minus losers: -0.07% a month (t = -0.15). Both extreme quintiles trail the
middle three. That shape is not what momentum predicts; it is what a volatility
effect would produce if the stocks with the most extreme twelve-month returns are
also the most volatile. The volatility sort in the next part of the study tests
that.

### 4.2 One month: continuation, not reversal

Monthly, 2016-06 to 2026-07, 122 months.

| | Q1 (losers) | Q2 | Q3 | Q4 | Q5 (winners) | Universe |
|---|---|---|---|---|---|---|
| Return per month | +0.60 | +1.09 | +1.02 | +1.59 | +1.21 | +1.10 |
| Turnover per month | 78% | 79% | 79% | 81% | 78% | |

The short-term reversal documented in developed markets (Jegadeesh, 1990) predicts
Q1 above Q5. The opposite holds. Losers minus winners is -0.61% a month (t = -1.89),
and nearly all of it is in the loser quintile: -0.50% a month against the universe
(t = -2.77). Turnover near 80% -- the level of a random reshuffle across five
quintiles -- shows that one-month returns barely persist as a ranking, so the effect
is a property of the month after a loss, not of a persistent group of stocks.

### 4.3 One week: nothing after a one-session delay

Weekly, 2016-07 to 2026-09, 529 weeks.

| | Q1 (losers) | Q2 | Q3 | Q4 | Q5 (winners) | Universe |
|---|---|---|---|---|---|---|
| Return per week | +0.20 | +0.34 | +0.27 | +0.28 | +0.14 | +0.25 |
| Turnover per week | 79% | 79% | 77% | 80% | 77% | |

Losers minus winners: +0.07% a week (t = +0.75).

### 4.4 The price limit, one session at a time

Next-session return of each stock relative to that session's universe mean, grouped
by the stock's close-to-close move today. Each day's group average is one
observation; t-statistics are Newey-West over days.

| Today's move | Stock-days | Next session vs universe | t |
|---|---|---|---|
| At or near the ceiling (>= +6.5%) | 26,705 | +1.694% | +39.47 |
| +3% to +6.5% | 59,234 | -0.388% | -22.54 |
| -3% to +3% | 658,580 | -0.052% | -11.26 |
| -6.5% to -3% | 51,644 | +0.728% | +31.50 |
| At or near the floor (<= -6.5%) | 21,459 | -0.225% | -3.77 |

The sign flips at the band. A rise of 3% to 6.5% gives back 0.39% the next session;
a rise that reaches the limit adds another 1.69%. The same holds, more weakly, on the
downside. Inside the band, a large close-to-close move overshoots and partly
reverses, as short-term reversal predicts. At the band, the close is not a market
clearing price: the stock stops at the limit with excess demand (or supply)
outstanding, and the next session completes the move.

None of this is a trading strategy. The +1.69% is measured from a close at which the
stock could not be bought -- a ceiling-locked stock has sellers queued at no price
below the limit -- and the reversal inside the band is a close-to-close measurement
exposed to closing-auction effects that daily data cannot separate. The weekly and
monthly sorts enter one session late for exactly this reason, and 4.3 shows what
remains.

The same mechanism shows up in the sorts: in the session immediately after a weekly
formation, last week's winners beat the universe by 0.13% (t = +4.0) and its losers
trail it by 0.10% (t = -3.1). The extreme quintiles are where the limit-hitting
stocks are.

### 4.5 After costs

Long leg minus the universe, per period, net of costs (t in brackets).

| Strategy | Long leg | 0.2% round trip | 0.4% round trip | 0.6% round trip | Long-leg turnover |
|---|---|---|---|---|---|
| Momentum 12-1, monthly | Q5 | -0.18 (-0.68) | -0.23 (-0.86) | -0.28 (-1.05) | 24% |
| One-month, monthly | Q1 | -0.65 (-3.65) | -0.81 (-4.54) | -0.97 (-5.43) | 78% |
| One-week, weekly | Q1 | -0.20 (-4.12) | -0.36 (-7.38) | -0.52 (-10.67) | 79% |

Gross of costs, no long leg beats the universe either (momentum -0.13%, t = -0.49;
one-month -0.50%, t = -2.77; one-week -0.04%, t = -0.88). Weekly rebalancing at 79%
turnover costs about 0.32% a week at 0.4% round trip, roughly 16% a year.

### 4.6 Robustness

Long minus short, per period (t):

| Strategy | Enter at the formation close | Enter one session later |
|---|---|---|
| Momentum 12-1 | -0.09 (-0.19) | -0.07 (-0.15) |
| One-month | -0.44 (-1.21) | -0.61 (-1.89) |
| One-week | -0.09 (-1.04) | +0.07 (+0.75) |

| Strategy | First half | Second half | Split |
|---|---|---|---|
| Momentum 12-1 | +0.24 (+0.34) | -0.38 (-0.57) | 2021-11 |
| One-month | -0.87 (-1.76) | -0.35 (-0.77) | 2021-07 |
| One-week | -0.02 (-0.14) | +0.15 (+1.23) | 2021-07 |

The one-month continuation is present in both halves but weaker in the second, and
neither half is significant on its own. Momentum is absent in both.

## 5. Interpretation

Three statements are supported by the data here.

1. Twelve-month momentum, the most robust anomaly in developed markets, is absent on
   HOSE in 2017-2026, before and after 2021.
2. One-month returns continue rather than reverse, concentrated in the loser
   quintile, and survivorship bias works against this finding.
3. At a one-session horizon, predictability is large and organised by the price
   limit: reversal inside the band, continuation at it.

What the data does not settle is the mechanism behind the one-month continuation.
The limit accounts for the session after a limit hit, but the monthly effect remains
after skipping that session, so it is not only spillover. Delayed price discovery
across several limit days, retail herding and slow information diffusion all predict
it; distinguishing them needs order-flow or ownership data.

## 6. Limitations

- **Survivorship.** Current listing only (section 2).
- **Equal weights.** Without a history of shares outstanding there is no market
  capitalisation, so the smallest stocks weigh as much as the largest. The size
  family needs that history before value-weighted results can be reported.
- **Limit days in the sorts.** A stock locked at its limit on an entry or exit date
  cannot actually be traded at that close. The sorts assume it can.
- **Cost model.** A single proportional cost, with no market impact. Small, illiquid
  stocks would cost more.
- **Adjustment method.** The provider's adjustment procedure is undocumented. It
  agrees with a second provider on 99.8% of days, but both could share an error.

## 7. Reproduction

```
pip install -r requirements.txt
python -m factors.ingest      # downloads everything into data/, about 10 minutes
python -m factors.trend       # every table in section 4
python -m pytest -q
```

`factors.ingest` always performs a full refresh. Adjusted prices are restated
backwards whenever a stock pays a stock dividend, so appending new days to old
history would splice two adjustment bases together.

## 8. Next

| Family | Signals | Available from daily data | Needs |
|---|---|---|---|
| Liquidity | Amihud illiquidity, high-low spread (Corwin-Schultz), turnover, size | Amihud needs traded value; the high-low spread needs only prices | A history of shares outstanding for turnover and size, and an unadjusted price or value series for Amihud |
| Volatility | Idiosyncratic volatility, beta | Both, with a Dimson correction for thin trading | Nothing further |

Because short selling is prohibited, the implementable form of any of these is a
long-only portfolio hedged with VN30 index futures; the cost of that hedge is
modelled in the companion repository on VN30 futures.

## 9. Repository

```
factors/
  config.py     paths, market rules, cost and eligibility assumptions
  kbs.py        client for the provider's endpoints: listing, profiles, daily bars
  ingest.py     full download into data/
  panel.py      HOSE-era price panel, market calendar, out-of-band flags
  signals.py    period ends, momentum and reversal signals, eligibility
  sorts.py      quintile portfolios with a skip day, turnover, costs
  stats.py      Newey-West t-statistics
  trend.py      the study: every table in section 4
tests/
  test_factors.py   no look-ahead at entry, momentum skip month, out-of-band
                    rule across trading gaps, unfinished periods, costs, inference
```
