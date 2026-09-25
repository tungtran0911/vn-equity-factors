"""The monthly cross-section: every characteristic, ranked, on common stocks.

One place builds the stock-by-month table that the Fama-MacBeth regressions, the
walk-forward and the frozen model all read, so none of them can drift apart on a
definition.

A stock-month enters only if the stock is eligible for every characteristic, so a
comparison between specifications is never a comparison between samples. Each
characteristic is converted to a cross-sectional percentile rank in [0, 1] month by
month: ranks are comparable across characteristics and across time, and immune to
the outliers a band-censored, survivorship-affected return series produces.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from factors.panel import Panel
from factors.risk import risk_signals
from factors.signals import trend_signals
from factors.sorts import holding_returns

FEATURES = ("momentum", "momentum_extremity", "one_month", "ivol", "beta",
            "limit_up_days")


@dataclass
class CrossSection:
    dates: pd.DatetimeIndex          # month-end formation dates
    eligible: pd.DataFrame           # formation x stock, eligible for everything
    raw: dict[str, pd.DataFrame]     # characteristics in their own units
    ranks: dict[str, pd.DataFrame]   # percentile ranks, NaN where not eligible
    hold: pd.DataFrame               # next-period return, formation x stock


def pct_rank(frame: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional percentile rank in [0, 1], date by date."""
    r = frame.rank(axis=1)
    return r.sub(1).div(r.max(axis=1).sub(1), axis=0)


def build(panel: Panel, trend: dict | None = None,
          risk: dict | None = None) -> CrossSection:
    trend = trend if trend is not None else trend_signals(panel)
    risk = risk if risk is not None else risk_signals(panel)
    mom, mom_el = trend["momentum_12_1"]
    rev, rev_el = trend["reversal_1m"]
    dates = risk["ivol"][0].index.intersection(mom.index).intersection(rev.index)
    eligible = (mom_el.reindex(dates) & rev_el.reindex(dates)
                & risk["ivol"][1].reindex(dates)
                & risk["beta_dimson"][1].reindex(dates))
    raw = {"momentum": mom, "one_month": rev, "ivol": risk["ivol"][0],
           "beta": risk["beta_dimson"][0], "limit_up_days": risk["ceiling_hits"][0]}
    raw = {k: v.reindex(dates) for k, v in raw.items()}
    ranks = {k: pct_rank(v.where(eligible)) for k, v in raw.items()}
    # Distance from the middle of the momentum distribution: both tails score 1.
    ranks["momentum_extremity"] = (ranks["momentum"] - 0.5).abs() * 2
    return CrossSection(dates=dates, eligible=eligible, raw=raw, ranks=ranks,
                        hold=holding_returns(panel, dates, skip=1))
