"""Beta, idiosyncratic volatility and lottery demand on HOSE.

    python -m factors.volatility

Three hypotheses, each with a sharper prediction on HOSE than in markets where
short selling is allowed:

  Betting against beta (Frazzini and Pedersen, 2014). Investors who cannot or will
  not borrow buy high-beta stocks for exposure, pushing their prices up and their
  returns down. Predicts a flat or negative beta-return relation.

  The idiosyncratic volatility puzzle (Miller, 1977; Stambaugh, Yu and Yuan, 2015).
  Where opinions differ and short selling is costly, prices reflect the optimists;
  volatile stocks are where opinions differ most, so they are overpriced, and the
  arbitrage that would correct it is a short sale. HOSE prohibits short selling
  outright, so the prediction is a negative ivol-return relation that sits in the
  high-ivol quintile's underperformance, not in the low-ivol quintile's gain.

  Lottery demand (Bali, Cakici and Whitelaw, 2011). Investors overpay for a small
  chance of an extreme gain, measured by the month's largest daily return. On HOSE
  the largest possible daily gain is the 7% limit, so the measure saturates; the
  count of limit-up days is the version the market allows.

Then the test the trend study left open: whether the extreme momentum quintiles
trail the middle because they are the volatile stocks.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from factors.config import MARKET, RISK_FREE, RISK_FREE_GRID
from factors.panel import load
from factors.report import (cost_section, pct, quintile_section, subperiod_section,
                            summary_section)
from factors.risk import risk_signals
from factors.signals import trend_signals
from factors.sorts import N_QUANTILES, holding_returns, quintile_backtest, quintile_labels
from factors.stats import capm_nw, fama_macbeth, newey_west

# Low-risk quintile held long in every case: each hypothesis predicts it earns more.
STRATEGIES = {
    "beta_dimson": (1, N_QUANTILES, 12),
    "ivol": (1, N_QUANTILES, 12),
    "max": (1, N_QUANTILES, 12),
}
Q = range(1, N_QUANTILES + 1)
SIGNAL_FORMAT = {
    "beta_dimson": lambda x: f"{x:.2f}",
    "ivol": lambda x: f"{x * np.sqrt(250):.0%} a year",
    "max": lambda x: f"{x:.1%}",
}


def _by_quintile(labels: pd.DataFrame, values: pd.DataFrame, fmt) -> list[str]:
    """Time-series average of each quintile's cross-sectional mean of `values`."""
    v = values.reindex(index=labels.index, columns=labels.columns)
    return [fmt(v.where(labels == k).mean(axis=1).mean()) for k in Q]


def beta_section(risk) -> None:
    ols = risk["beta_ols"][0].where(risk["beta_ols"][1]).stack()
    dim = risk["beta_dimson"][0].where(risk["beta_dimson"][1]).stack()
    print("\n## Beta estimates against VN-Index, 250 sessions\n")
    print(f"same-day (OLS) beta: mean {ols.mean():.3f}, median {ols.median():.3f}; "
          f"Dimson beta: mean {dim.mean():.3f}, median {dim.median():.3f}; "
          f"Dimson above OLS in {(dim > ols).mean():.0%} of {len(dim):,} "
          f"stock-months")


def leg_section(results: dict[str, pd.DataFrame]) -> None:
    print("\n## Where the spread sits: each extreme quintile against the universe, "
          "per month (t)\n")
    print("| signal | Q1 (low) - universe | Q5 (high) - universe |")
    print("|---|---|---|")
    for name, bt in results.items():
        cells = [f"{pct(m)} ({t:+.2f})" for m, t in
                 (newey_west(bt["Q1"] - bt["universe"]),
                  newey_west(bt[f"Q{N_QUANTILES}"] - bt["universe"]))]
        print(f"| {name} | " + " | ".join(cells) + " |")


def alpha_section(panel, results: dict[str, pd.DataFrame]) -> None:
    """CAPM alphas. Betting against beta is a claim about risk-adjusted returns:
    over 2017-2026 the index more than doubled, so high-beta stocks earned more
    in raw terms simply by carrying more market exposure."""
    mkt = (pd.read_parquet(MARKET).sort_values("date").set_index("date")["close"]
             .reindex(panel.calendar).ffill())
    print("\n## CAPM alphas of the long-short spread (Q1 - Q5) and each leg, "
          "per month (t)\n")
    print("| strategy | spread beta | alpha, rf 0% | alpha, rf 4% | alpha, rf 6% "
          "| Q1 alpha, rf 4% | Q5 alpha, rf 4% |")
    print("|---|---|---|---|---|---|---|")
    for name, bt in results.items():
        rm = mkt.loc[bt["exit"]].to_numpy() / mkt.loc[bt["entry"]].to_numpy() - 1
        years = (bt["exit"] - bt["entry"]).dt.days.to_numpy() / 365
        spread = bt["Q1"] - bt[f"Q{N_QUANTILES}"]
        cells, beta = [], None
        for rf_annual in RISK_FREE_GRID:
            rf = (1 + rf_annual) ** years - 1
            a, t, beta = capm_nw(spread, pd.Series(rm - rf, index=bt.index))
            cells.append(f"{pct(a)} ({t:+.2f})")
        rf = (1 + RISK_FREE) ** years - 1
        for q in ("Q1", f"Q{N_QUANTILES}"):
            a, t, _ = capm_nw(bt[q] - rf, pd.Series(rm - rf, index=bt.index))
            cells.append(f"{pct(a)} ({t:+.2f})")
        print(f"| {name} | {beta:+.2f} | " + " | ".join(cells) + " |")


def ceiling_section(panel, risk) -> None:
    hits, elig = risk["ceiling_hits"]
    hold = holding_returns(panel, hits.index, skip=1)
    groups = [(0, 0, "0"), (1, 1, "1"), (2, 2, "2"), (3, 99, "3 or more")]
    series = {label: [] for *_, label in groups}
    counts = {label: 0 for *_, label in groups}
    for f in hold.index:
        h = hits.loc[f][elig.loc[f]].dropna()
        r = hold.loc[f, h.index].dropna()
        h = h.loc[r.index]
        for lo, hi, label in groups:
            members = h[(h >= lo) & (h <= hi)].index
            counts[label] += len(members)
            if len(members) >= 5:
                series[label].append(r.loc[members].mean() - r.mean())
    total = sum(counts.values())
    print("\n## Limit-up days in the formation month: next month vs the universe\n")
    print("| limit-up days | share of stock-months | months with 5+ stocks "
          "| next month - universe (%) | t |")
    print("|---|---|---|---|---|")
    for *_, label in groups:
        m, t = newey_west(pd.Series(series[label]))
        print(f"| {label} | {counts[label] / total:.1%} | {len(series[label])} "
              f"| {pct(m)} | {t:+.2f} |")


def _pct_rank(frame: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional percentile rank in [0, 1], date by date."""
    r = frame.rank(axis=1)
    return r.sub(1).div(r.max(axis=1).sub(1), axis=0)


def momentum_test(panel, trend, risk) -> None:
    mom, mom_el = trend["momentum_12_1"]
    rev, rev_el = trend["reversal_1m"]
    dates = (risk["ivol"][0].index.intersection(mom.index)
             .intersection(rev.index))
    common = (mom_el.reindex(dates) & rev_el.reindex(dates)
              & risk["ivol"][1].reindex(dates) & risk["beta_dimson"][1].reindex(dates))
    raw = {"momentum": mom, "one_month": rev, "ivol": risk["ivol"][0],
           "beta": risk["beta_dimson"][0], "limit_up_days": risk["ceiling_hits"][0]}
    ranks = {k: _pct_rank(v.reindex(dates).where(common)) for k, v in raw.items()}
    ranks["momentum_extremity"] = (ranks["momentum"] - 0.5).abs() * 2
    hold = holding_returns(panel, dates, skip=1)

    labels = quintile_labels(hold, mom.reindex(dates), common)
    print("\n## Are the extreme momentum quintiles the volatile ones?\n")
    print("| | " + " | ".join(f"Q{k}" for k in Q) + " |")
    print("|---" * (N_QUANTILES + 1) + "|")
    print("| ivol, annualised | " + " | ".join(_by_quintile(
        labels, raw["ivol"], lambda x: f"{x * np.sqrt(250):.0%}")) + " |")
    print("| Dimson beta | " + " | ".join(_by_quintile(
        labels, raw["beta"], lambda x: f"{x:.2f}")) + " |")
    print("| limit-up days per month | " + " | ".join(_by_quintile(
        labels, raw["limit_up_days"], lambda x: f"{x:.2f}")) + " |")

    specs = [
        ["momentum", "momentum_extremity", "one_month"],
        ["momentum", "momentum_extremity", "one_month", "ivol", "beta"],
        ["momentum", "momentum_extremity", "one_month", "ivol", "beta",
         "limit_up_days"],
    ]
    fits = [fama_macbeth(hold, {k: ranks[k] for k in spec}) for spec in specs]
    names = specs[-1]
    print(f"\n## Fama-MacBeth: next-month return on percentile ranks, "
          f"{len(fits[0])} months, same stocks in every column\n")
    print("Each coefficient is the difference in monthly return, in percent, "
          "between the lowest- and highest-ranked stock. t in brackets.\n")
    print("| rank of | (1) | (2) | (3) |")
    print("|---|---|---|---|")
    for k in names:
        cells = []
        for fit in fits:
            if k in fit:
                m, t = newey_west(fit[k])
                cells.append(f"{pct(m)} ({t:+.2f})")
            else:
                cells.append("")
        print(f"| {k} | " + " | ".join(cells) + " |")

    # Two thirds of stocks have no limit-up day and share one tied rank, so the
    # coefficient's "lowest to highest" span overstates the real contrast.
    hits = raw["limit_up_days"].reindex(dates).where(common)
    r0 = ranks["limit_up_days"].where(hits == 0).stack().mean()
    r3 = ranks["limit_up_days"].where(hits >= 3).stack().mean()
    coef, _ = newey_west(fits[-1]["limit_up_days"])
    print(f"\nlimit-up days: mean rank {r0:.3f} with none, {r3:.3f} with three or "
          f"more; implied difference in (3) {pct(coef * (r3 - r0))} a month")

    full = fits[-1]
    half = len(full) // 2
    print(f"\n## Specification (3) by half, split at {full.index[half].date()}\n")
    print("| rank of | first half | second half |")
    print("|---|---|---|")
    for k in names:
        cells = [f"{pct(m)} ({t:+.2f})" for m, t in
                 (newey_west(full[k].iloc[:half]), newey_west(full[k].iloc[half:]))]
        print(f"| {k} | " + " | ".join(cells) + " |")


def run() -> int:
    panel = load()
    risk = risk_signals(panel)
    trend = trend_signals(panel)

    beta_section(risk)
    results = {}
    for name in STRATEGIES:
        sig, elig = risk[name]
        bt = quintile_backtest(panel, sig, elig, skip=1)
        results[name] = bt
        labels = quintile_labels(holding_returns(panel, sig.index, 1), sig, elig)
        near_limit = (risk["ceiling_hits"][0] > 0).astype(float)
        quintile_section(name, bt, {
            "mean signal": _by_quintile(labels, sig, SIGNAL_FORMAT[name]),
            "share with a limit-up day": _by_quintile(labels, near_limit,
                                                      lambda x: f"{x:.0%}"),
        })
    summary_section(results, STRATEGIES)
    alpha_section(panel, results)
    leg_section(results)
    cost_section(results, STRATEGIES)
    subperiod_section(results, STRATEGIES)
    ceiling_section(panel, risk)
    momentum_test(panel, trend, risk)
    return 0


if __name__ == "__main__":
    sys.exit(run())
