"""Beta, idiosyncratic volatility and the lottery signal at month-end formation.

  beta_ols      slope of daily stock returns on VN-Index returns over the 250
                sessions before formation. Reported to show the size of the
                thin-trading bias below; not sorted on.
  beta_dimson   the sum of slopes on the market's return the day before, the same
                day and the day after (Dimson, 1979). A stock that trades
                infrequently reflects market news a day late, so a same-day slope
                understates its beta. The window ends the day BEFORE formation:
                the "day after" term at the last date of the window then uses the
                formation-day market return, which is known at the formation close.
  ivol          standard deviation of residuals from a market-model regression on
                the formation month's daily returns (Ang, Hodrick, Xing and Zhang,
                2006, with one factor: there is no book-value or market-cap history
                here for the other two).
  max           the largest daily return in the formation month (Bali, Cakici and
                Whitelaw, 2011). On HOSE it cannot exceed the 7% limit, and about
                three stock-months in ten reach 6.5% or more, so the top of its
                distribution is a pile-up at the ceiling ordered by tick rounding.
  ceiling_hits  the number of days in the formation month that closed at or near
                the ceiling (+6.5% or more). In a band-limited market this, not
                MAX, is what distinguishes one lottery-like stock from another.

Daily returns are censored at the band, so ivol and max understate the true
dispersion of the stocks that hit limits most often. That censoring works against
finding any volatility effect: the most volatile stocks look calmer than they are.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.config import MARKET
from factors.panel import Panel
from factors.signals import eligibility, period_ends

BETA_WINDOW = 250
BETA_MIN_OBS = 200
MONTH_MIN_OBS = 15
NEAR_LIMIT = 0.065   # a close within tick rounding of the 7% band


def market_returns(calendar: pd.DatetimeIndex) -> pd.Series:
    m = (pd.read_parquet(MARKET).sort_values("date")
           .set_index("date")["close"].reindex(calendar))
    return m / m.shift(1) - 1


def _ols(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Coefficients (intercept first) and residuals of y on [1, x]."""
    X = np.column_stack([np.ones(len(y)), x])
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    return coef, y - X @ coef


def risk_signals(panel: Panel, market: pd.Series | None = None
                 ) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """{name: (signal, eligible)} on month-ends with a full year of history.

    `market` is daily market returns on the panel's calendar; VN-Index by default.
    """
    rm = (market_returns(panel.calendar) if market is None
          else market.reindex(panel.calendar)).to_numpy()
    ret = panel.ret.to_numpy()
    pos = panel.calendar.get_indexer
    months = period_ends(panel.calendar, "M")
    idx = pos(months)
    keep = idx >= BETA_WINDOW + 1
    formation, idx = months[keep], idx[keep]
    prev_month = months[np.flatnonzero(keep) - 1]

    out = {k: np.full((len(formation), ret.shape[1]), np.nan)
           for k in ("beta_ols", "beta_dimson", "ivol", "max", "ceiling_hits")}
    for row, (i, p) in enumerate(zip(idx, pos(prev_month))):
        # Beta window t = i-250 .. i-1, with market lag t-1 and lead t+1 <= i.
        t = np.arange(i - BETA_WINDOW, i)
        mkt = np.column_stack([rm[t - 1], rm[t], rm[t + 1]])
        # Formation month for ivol and max: sessions after the previous month-end.
        u = np.arange(p + 1, i + 1)
        for j in range(ret.shape[1]):
            y = ret[t, j]
            ok = ~np.isnan(y) & ~np.isnan(mkt).any(axis=1)
            if ok.sum() >= BETA_MIN_OBS:
                out["beta_ols"][row, j] = _ols(y[ok], mkt[ok, 1])[0][1]
                out["beta_dimson"][row, j] = _ols(y[ok], mkt[ok])[0][1:].sum()
            y = ret[u, j]
            ok = ~np.isnan(y) & ~np.isnan(rm[u])
            if ok.sum() >= MONTH_MIN_OBS:
                resid = _ols(y[ok], rm[u][ok])[1]
                out["ivol"][row, j] = resid.std(ddof=2)
                out["max"][row, j] = y[ok].max()
                out["ceiling_hits"][row, j] = (y[ok] >= NEAR_LIMIT).sum()

    cols = panel.close.columns
    frames = {k: pd.DataFrame(v, index=formation, columns=cols) for k, v in out.items()}
    year_start = panel.calendar[idx - BETA_WINDOW - 1]
    long_elig = eligibility(panel, formation, year_start)
    month_elig = eligibility(panel, formation, prev_month)
    return {"beta_ols": (frames["beta_ols"], long_elig),
            "beta_dimson": (frames["beta_dimson"], long_elig),
            "ivol": (frames["ivol"], month_elig),
            "max": (frames["max"], month_elig),
            "ceiling_hits": (frames["ceiling_hits"], month_elig)}
