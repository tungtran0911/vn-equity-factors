# HOSE Equities: The Daily Price Limit and the Cross-Section of Returns

Which stock characteristics predict returns on the Ho Chi Minh Stock Exchange, and
why? This study tests two families of characteristics -- past returns (momentum and
short-term reversal) and risk (beta, idiosyncratic volatility, lottery-like payoffs)
-- against theories developed for markets that allow short selling and have no daily
price limit. HOSE has neither, and both differences turn out to matter.

**Trend.** Twelve-month momentum is absent (-0.07% a month, t = -0.15). One-month
returns continue rather than reverse: last month's losers trail the equal-weighted
universe by 0.50% a month (t = -2.77). At a one-session horizon returns are
organised by the +/-7% price limit -- a stock that closes at its ceiling gains a
further 1.69% the next session (t = 39), while one that rises 3% to 6.5% gives back
0.39% (t = -23). Large moves inside the band reverse; moves the band truncates
continue.

**Risk.** The low-beta and low-volatility anomalies do not appear in raw returns,
because the market more than doubled over the sample and high-risk stocks carried
more of it. After a CAPM adjustment every low-minus-high spread is positive, as the
theories predict, but none is significant. In cross-sectional regressions the
idiosyncratic volatility effect (-1.17, t = -2.54) is absorbed by one HOSE-specific
characteristic: the number of days in the month a stock closed at its ceiling.
Holding past returns, beta and volatility fixed, a stock with three or more limit-up
days earns 0.69% a month less the following month than a stock with none, and the
effect has the same sign and size before and after 2022. The one-month continuation
survives the same controls (+1.17, t = +2.32).

The daily price limit is the common thread. It turns the largest daily gain -- the
standard measure of lottery demand -- into a count of limit-up days, and the count is
what prices. No long-only portfolio in this study beats the universe after costs;
the findings are about how HOSE prices risk and attention, not about a trading
strategy.

---

## 1. Market structure

| | |
|---|---|
| Exchange | Ho Chi Minh Stock Exchange (HOSE), about 400 listed stocks |
| Daily price limit | +/-7% of the reference price (the previous close) |
| Short selling | not permitted; a long-short spread is not a position anyone can hold |
| Trading cost assumed | 0.4% round trip: brokerage of about 0.15% per side plus 0.1% personal income tax on sales. Brokerage varies by broker, so results are also shown at 0.2% and 0.6% |
| Risk-free rate assumed | 4% a year for CAPM alphas; there is no short-rate series in the data, so alphas are also shown at 0% and 6% |

When the price that clears supply and demand lies outside the band, the stock closes
at the limit with orders unfilled on one side, and that imbalance carries into the
next session. On Vietnamese price boards a close at the ceiling is displayed in its
own colour.

## 2. Data

**Source.** Daily bars for every stock currently listed on HOSE, and for VN-Index,
from KBS's public endpoints, called directly: 887,291 bars for 404 of 405 stocks (one,
SBV, failed to download), 2016-01-04 to 2026-09-25.

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

**Survivorship.** The universe is today's listing. Stocks delisted between 2016 and
2026 are absent. Delisted stocks are disproportionately past losers and distressed,
volatile names, so the bias raises the measured returns of loser and high-risk
portfolios. It works against the loser underperformance in 4.2 and probably against
the negative price of limit-up days in 5.5.

**Eligibility.** At each formation date a stock enters only if, over the signal
window plus the preceding 60 sessions, it was HOSE-listed, traded on at least 95% of
market days, and never moved beyond the band between consecutive sessions. The
provider omits days without trades rather than recording zero volume, so tradability
is measured against the market calendar. On average 255 to 277 stocks are eligible
per formation date.

## 3. Method

**Portfolios.** Eligible stocks are ranked on a characteristic and split into
equal-weighted quintiles, Q1 holding the lowest values. Positions are entered at the
close one session after formation and held to the close one session after the next
formation date. Without that skip the signal and the entry would share a closing
price, and any move in the following session -- including the price-limit spillover
of 4.4 -- would be credited to a strategy that could not have traded it.

**Long leg, short leg.** The long leg is the quintile a theory says to buy. The
long-short spread describes the cross-section; the implementable quantity is the
long leg's return over the equal-weighted universe, after costs. Turnover is the
share of a quintile's names that are new at each rebalance; each rebalance costs
turnover times the round-trip cost.

**Risk adjustment.** CAPM alphas from time-series regressions of portfolio returns on
VN-Index returns over the same holding periods.

**Joint tests.** Fama-MacBeth regressions: each month, next month's return is
regressed across stocks on the percentile ranks of several characteristics at once;
the reported coefficient is the time-series mean of the monthly slopes. Ranks make
the coefficients comparable (each is the return difference between the lowest- and
highest-ranked stock) and insensitive to outliers. Every specification uses the same
stocks.

**Inference.** Newey-West standard errors with lag length floor(4 (T/100)^(2/9)),
for portfolio means, CAPM intercepts and Fama-MacBeth slopes alike.

## 4. Trend

### 4.1 Twelve-month momentum: nothing

Return from month-end t-12 to t-1, skipping the latest month. Monthly, 2017-03 to
2026-07, 113 months; mean return per month in percent.

| | Q1 (losers) | Q2 | Q3 | Q4 | Q5 (winners) | Universe |
|---|---|---|---|---|---|---|
| Return per month | +1.23 | +1.38 | +1.35 | +1.33 | +1.16 | +1.29 |
| Turnover per month | 27% | 52% | 55% | 49% | 24% | |

Winners minus losers: -0.07% a month (t = -0.15). Both extreme quintiles trail the
middle three -- a shape momentum does not predict. Section 5.6 shows it is mostly a
volatility effect.

### 4.2 One month: continuation, not reversal

Monthly, 2016-06 to 2026-07, 122 months.

| | Q1 (losers) | Q2 | Q3 | Q4 | Q5 (winners) | Universe |
|---|---|---|---|---|---|---|
| Return per month | +0.60 | +1.09 | +1.02 | +1.59 | +1.21 | +1.10 |
| Turnover per month | 78% | 79% | 79% | 81% | 78% | |

Short-term reversal (Jegadeesh, 1990) predicts Q1 above Q5; the opposite holds.
Losers minus winners is -0.61% a month (t = -1.89), and nearly all of it is in the
loser quintile: -0.50% a month against the universe (t = -2.77). Turnover near 80%,
the level of a random reshuffle across five quintiles, shows the effect is a
property of the month after a loss, not of a persistent group of stocks.

### 4.3 One week: nothing after a one-session delay

Weekly, 2016-07 to 2026-09, 529 weeks. Returns per week: +0.20, +0.34, +0.27,
+0.28, +0.14 for Q1 to Q5, universe +0.25. Losers minus winners +0.07% a week
(t = +0.75).

### 4.4 The price limit, one session at a time

Next-session return of each stock relative to that session's universe mean, grouped
by the stock's move today. Each day's group average is one observation.

| Today's move | Stock-days | Next session vs universe | t |
|---|---|---|---|
| At or near the ceiling (>= +6.5%) | 26,705 | +1.694% | +39.47 |
| +3% to +6.5% | 59,234 | -0.388% | -22.54 |
| -3% to +3% | 658,580 | -0.052% | -11.26 |
| -6.5% to -3% | 51,644 | +0.728% | +31.50 |
| At or near the floor (<= -6.5%) | 21,459 | -0.225% | -3.77 |

The sign flips at the band. Inside it, a large close-to-close move overshoots and
partly reverses. At it, the close is not a market-clearing price, and the next session
completes the move. None of this is tradeable at the close: a ceiling-locked stock
has sellers queued at no price below the limit, and the reversal inside the band is a
close-to-close measurement exposed to closing-auction effects daily data cannot
separate. The weekly and monthly sorts enter one session late for this reason. In the
session they skip, last week's winners beat the universe by 0.13% (t = +4.0) and its
losers trail it by 0.10% (t = -3.1).

### 4.5 After costs

Long leg minus the universe, per period, net of costs (t):

| Strategy | Long leg | 0.2% round trip | 0.4% | 0.6% | Long-leg turnover |
|---|---|---|---|---|---|
| Momentum 12-1, monthly | Q5 | -0.18 (-0.68) | -0.23 (-0.86) | -0.28 (-1.05) | 24% |
| One-month, monthly | Q1 | -0.65 (-3.65) | -0.81 (-4.54) | -0.97 (-5.43) | 78% |
| One-week, weekly | Q1 | -0.20 (-4.12) | -0.36 (-7.38) | -0.52 (-10.67) | 79% |

Long minus short by half (t): momentum +0.24 (+0.34) then -0.38 (-0.57); one-month
-0.87 (-1.76) then -0.35 (-0.77); one-week -0.02 (-0.14) then +0.15 (+1.23). Entering
at the formation close instead of a session later changes none of the conclusions.

## 5. Volatility and lottery demand

### 5.1 Hypotheses

| Characteristic | Theory | Mechanism | Prediction on HOSE |
|---|---|---|---|
| Beta | Betting against beta (Frazzini and Pedersen, 2014) | Investors who cannot borrow buy high-beta stocks for exposure and bid them up | Low-beta alpha above high-beta alpha |
| Idiosyncratic volatility | Miller (1977); Stambaugh, Yu and Yuan (2015) | Where opinions differ and shorting is costly, prices reflect the optimists; nobody can sell the overpricing away | Negative, concentrated in the high-volatility quintile; strongest where shorting is banned outright |
| Largest daily gain (MAX) | Lottery demand (Bali, Cakici and Whitelaw, 2011) | Investors overpay for a small chance of an extreme gain | Negative; but MAX cannot exceed the 7% limit on HOSE |

**Estimation.** Beta uses the 250 sessions before formation. Stocks that trade
infrequently respond to market news a day late, so the same-day regression slope
understates their beta; the Dimson (1979) estimator sums the slopes on the market's
return the day before, the same day and the day after. The estimation window ends the
day before formation, so the "day after" term never reaches past the formation
close. Across 28,876 stock-months the same-day beta averages 0.782 and the Dimson beta
0.843; Dimson is higher in 59% of cases. Idiosyncratic volatility is the standard
deviation of residuals from a market-model regression on the formation month's daily
returns (Ang, Hodrick, Xing and Zhang, 2006, with one factor: there is no book or
market-cap history for the other two). MAX is the formation month's largest daily
return.

**The limit changes the lottery measure.** 31% of eligible stock-months have at least
one close at or above +6.5%, so the top of the MAX distribution is a pile-up at the
ceiling, ordered by tick rounding. What distinguishes one lottery-like stock from
another on HOSE is how often it hit the limit. The study adds that count: the number
of days in the formation month that closed at +6.5% or more.

Daily returns are censored at the band, so volatility and MAX understate the true
dispersion of the stocks that hit limits most. That works against finding any effect.

### 5.2 Sorts

Monthly, 2017-04 to 2026-07, 112 months; mean return per month in percent.

| Beta (Dimson) | Q1 (low) | Q2 | Q3 | Q4 | Q5 (high) | Universe |
|---|---|---|---|---|---|---|
| Return | +0.90 | +1.42 | +1.40 | +1.55 | +1.26 | +1.30 |
| Mean beta | 0.17 | 0.53 | 0.81 | 1.09 | 1.50 | |
| Share with a limit-up day | 21% | 25% | 31% | 34% | 41% | |

| Idiosyncratic volatility | Q1 (low) | Q2 | Q3 | Q4 | Q5 (high) | Universe |
|---|---|---|---|---|---|---|
| Return | +1.08 | +1.51 | +1.39 | +1.11 | +0.90 | +1.20 |
| Mean, annualised | 14% | 22% | 29% | 36% | 52% | |
| Share with a limit-up day | 2% | 7% | 21% | 45% | 78% | |

| MAX | Q1 (low) | Q2 | Q3 | Q4 | Q5 (high) | Universe |
|---|---|---|---|---|---|---|
| Return | +0.95 | +1.26 | +1.53 | +1.13 | +1.11 | +1.20 |
| Mean MAX | 2.0% | 3.3% | 4.6% | 5.9% | 6.9% | |
| Share with a limit-up day | 1% | 2% | 10% | 46% | 95% | |

In raw returns none of the three works as the theories predict. The low-beta
quintile earns the least (-0.40% a month against the universe, t = -1.15). The
high-volatility quintile trails the universe by 0.29% (t = -1.15) and the low one by
0.12% (t = -0.45): the spread sits on the high side, as Stambaugh, Yu and Yuan
predict, but weakly. Every low-minus-high spread changes sign between the two halves
of the sample (beta -1.40 then +0.67; volatility -0.67 then +1.03; MAX -0.94 then
+0.61, split at 2021-12), which is the signature of market exposure rather than
mispricing.

### 5.3 Risk-adjusted

VN-Index rose from 718 at the end of April 2017 to 1,736 at the end of July 2026,
with a 40% drawdown in 2022 on the way. A high-risk portfolio earns more in raw terms
in a rising market simply by carrying more of it. CAPM alphas
of the low-minus-high spread, per month (t):

| Spread (Q1 - Q5) | Spread beta | Alpha, rf 0% | Alpha, rf 4% | Alpha, rf 6% | Q1 alpha, rf 4% | Q5 alpha, rf 4% |
|---|---|---|---|---|---|---|
| Beta | -0.89 | +0.55 (+1.06) | +0.26 (+0.51) | +0.12 (+0.24) | +0.27 (+0.91) | +0.01 (+0.02) |
| Idiosyncratic volatility | -0.39 | +0.58 (+1.39) | +0.45 (+1.08) | +0.39 (+0.93) | +0.34 (+1.39) | -0.11 (-0.18) |
| MAX | -0.46 | +0.31 (+0.97) | +0.16 (+0.50) | +0.08 (+0.26) | +0.20 (+0.68) | +0.04 (+0.09) |

Every spread turns positive: low-risk stocks earn more than high-risk ones per unit of
market exposure, the direction all three theories predict. None is significant, and
the beta result depends on the assumed risk-free rate, because a spread with a beta of
-0.89 is mostly a bet on the market premium. The sorts cannot separate these
anomalies from zero on 112 months.

### 5.4 Limit-up days, one at a time

Next month's return against the universe, by the number of limit-up days in the
formation month:

| Limit-up days | Share of stock-months | Next month vs universe | t |
|---|---|---|---|
| 0 | 69.1% | -0.02% | -0.14 |
| 1 | 18.1% | -0.07% | -0.36 |
| 2 | 6.5% | -0.10% | -0.32 |
| 3 or more | 6.3% | -0.29% | -0.64 |

Monotonic, and insignificant. Section 5.5 shows why: the stocks with many limit-up
days are also last month's biggest winners, and one-month returns continue (4.2). In a
univariate sort the two effects offset.

### 5.5 Joint test

Fama-MacBeth regressions of next month's return on percentile ranks, 109 months, the
same stocks in every column. Each coefficient is the difference in monthly return, in
percent, between the lowest- and highest-ranked stock (t):

| Rank of | (1) | (2) | (3) |
|---|---|---|---|
| Momentum 12-1 | +0.05 (+0.09) | +0.29 (+0.51) | +0.30 (+0.53) |
| Momentum extremity | -0.52 (-1.47) | -0.22 (-0.64) | -0.25 (-0.73) |
| One-month return | +0.69 (+1.62) | +0.93 (+1.85) | +1.17 (+2.32) |
| Idiosyncratic volatility | | -1.17 (-2.54) | -0.44 (-0.88) |
| Beta (Dimson) | | +0.27 (+0.40) | +0.30 (+0.45) |
| Limit-up days | | | -1.18 (-2.59) |

Momentum extremity is |rank - 0.5| x 2, the distance from the middle of the momentum
distribution.

- Controlling for beta and past returns, idiosyncratic volatility carries a negative
  price (column 2). Adding limit-up days removes it (column 3): the volatility effect
  on HOSE is the limit-up effect.
- Limit-up days and the one-month return are both significant once they are in the
  same regression, with opposite signs. The same stocks carry a continuation that
  pays and a lottery premium that costs.
- Two thirds of stock-months have no limit-up day and share a tied rank (0.360);
  stocks with three or more average 0.946. The implied difference is 0.69% a month,
  about 8% a year, holding the other characteristics fixed.
- Beta carries no price in the cross-section, consistent with the flat raw-return
  relation that betting against beta explains, but not evidence for it.

### 5.6 Stability, and the momentum U-shape

Column (3) by half (t), split at 2022-01:

| Rank of | 2017-2021 | 2022-2026 |
|---|---|---|
| Limit-up days | -1.15 (-1.73) | -1.21 (-1.99) |
| One-month return | +1.25 (+1.60) | +1.09 (+1.64) |
| Idiosyncratic volatility | +0.43 (+0.51) | -1.30 (-3.32) |
| Beta (Dimson) | +1.23 (+1.43) | -0.62 (-0.63) |
| Momentum extremity | -0.38 (-0.71) | -0.13 (-0.29) |

The limit-up and one-month effects have the same sign and size in both halves, the
first dominated by the 2020-2021 retail boom and the second by the 2022 drawdown and
its recovery. The volatility effect exists only in the second half. Beta's price
follows the market: in a cross-sectional regression of realised returns on beta, the
slope is the realised market premium.

The momentum quintiles explain the U-shape of 4.1. The extremes are the risky stocks:

| Momentum quintile | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| Idiosyncratic volatility, annualised | 32% | 29% | 29% | 30% | 35% |
| Dimson beta | 0.91 | 0.79 | 0.77 | 0.78 | 0.85 |
| Limit-up days per month | 0.69 | 0.51 | 0.46 | 0.53 | 0.77 |

Controlling for volatility and beta cuts the extremity coefficient from -0.52 to
-0.22. It was never significant, and what remains of it is not.

## 6. Interpretation

Supported by the data:

1. Twelve-month momentum is absent on HOSE in 2017-2026, before and after 2021.
2. One-month returns continue, concentrated in the loser quintile; the effect survives
   controls for volatility, beta and limit-up days, and survivorship bias works
   against it.
3. At a one-session horizon returns reverse inside the price band and continue at it.
4. The negative price of idiosyncratic volatility is absorbed by the count of limit-up
   days, which carries a stable negative price of about 0.7% a month.
5. Beta and volatility anomalies point the way theory predicts after risk adjustment,
   but are not distinguishable from zero here.

Not settled: why limit-up stocks are overpriced. Three mechanisms predict it. Lottery
preference (Bali, Cakici and Whitelaw): a stock that hits the ceiling looks like a
ticket to an extreme gain. Attention (Barber and Odean, 2008): a ceiling close is the
most visible event on a Vietnamese price board, and individual investors buy what
catches their attention. Short-sale constraints (Miller): whatever the cause of the
overpricing, no one can sell it away. Separating them needs investor-level order flow
or ownership data. The one-month continuation has the same problem: delayed price
discovery across several limit days, herding and slow information diffusion all
predict it.

## 7. Limitations

- **Survivorship.** Current listing only (section 2).
- **Equal weights.** Without a history of shares outstanding there is no market
  capitalisation, so the smallest stocks weigh as much as the largest, and there is
  no size or value factor to put beside the market in the risk adjustment.
- **Risk-free rate.** Assumed, not observed; alphas are shown across a range.
- **Limit days in the sorts.** A stock locked at its limit on an entry or exit date
  cannot be traded at that close. The sorts assume it can.
- **Cost model.** A single proportional cost, with no market impact.
- **Multiple testing.** Six characteristics, several horizons and specifications were
  examined. Two results are significant in the joint regression and keep their sign
  and size in each half: the one-month continuation and the limit-up count. The
  one-month return was a pre-specified signal. The limit-up count was added after
  seeing how MAX behaves on HOSE, which is a reason to test it again on data it has
  not seen.

## 8. Reproduction

```
pip install -r requirements.txt
python -m factors.ingest        # downloads everything into data/, about 10 minutes
python -m factors.trend         # every table in section 4
python -m factors.volatility    # every table in section 5
python -m pytest -q
```

`factors.ingest` always performs a full refresh. Adjusted prices are restated
backwards whenever a stock pays a stock dividend, so appending new days to old
history would splice two adjustment bases together.

## 9. Next

- **Out-of-sample validation.** Fix the specification on data up to a cut-off, then
  test it once on the years after. The limit-up result is the first candidate.
- **Liquidity family.** Amihud illiquidity, the high-low spread estimator
  (Corwin-Schultz), turnover and size. The spread estimator needs only prices; the
  others need a history of shares outstanding and an unadjusted value series.
- **Hedged implementation.** Because short selling is prohibited, the implementable
  form of any of these is a long-only portfolio hedged with VN30 index futures; the
  cost of that hedge is modelled in the companion repository on VN30 futures.

## 10. Repository

```
factors/
  config.py       paths, market rules, cost and risk-free assumptions
  kbs.py          provider client: listing, profiles, daily bars, VN-Index
  ingest.py       full download into data/
  panel.py        HOSE-era price panel, market calendar, out-of-band flags
  signals.py      period ends, momentum and reversal signals, eligibility
  risk.py         Dimson and same-day beta, idiosyncratic volatility, MAX,
                  limit-up days
  sorts.py        holding-period returns, quintile assignment, portfolios, costs
  stats.py        Newey-West means, CAPM regressions, Fama-MacBeth
  report.py       tables shared by the studies
  trend.py        section 4
  volatility.py   section 5
tests/
  test_factors.py no look-ahead at entry, momentum skip month, out-of-band rule
                  across trading gaps, unfinished periods, costs, Dimson beta on a
                  lagged response, CAPM and Fama-MacBeth estimators
```
