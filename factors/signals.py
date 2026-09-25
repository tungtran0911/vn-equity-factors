"""Trend signals and their eligibility, measured at formation dates.

  momentum 12-1   return from month-end t-12 to month-end t-1. The most recent
                  month is skipped because one-month returns reverse; including
                  it would net two opposite effects into one number.
  reversal 1m     return over the last month.
  reversal 1w     return over the last week.

A stock is eligible at a formation date only if, over the whole window the signal
reads plus the 60-session tradability lookback, it was HOSE-listed, it traded on
at least 95% of market days, and no day's move exceeded the HOSE band. The last
condition catches both exchange transfers the listing date missed and residual
corporate-action errors in the adjusted prices.
"""

from __future__ import annotations

import pandas as pd

from factors.config import TRADED_LOOKBACK, TRADED_SHARE_MIN
from factors.panel import Panel


def period_ends(calendar: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    """Last trading day of each completed month ("M") or week ("W").

    The period the data ends in is dropped unless it is over: otherwise the last
    day of a half-finished month would pose as a month-end and a partial holding
    period would be counted as a full one.
    """
    s = pd.Series(calendar, index=calendar)
    ends = pd.DatetimeIndex(s.groupby(calendar.to_period(freq)).max().to_numpy())
    last = ends[-1]
    if (last + pd.offsets.BDay(1)).to_period(freq) == last.to_period(freq):
        ends = ends[:-1]
    return ends


def _eligible(panel: Panel, formation: pd.DatetimeIndex,
              window_start: pd.DatetimeIndex) -> pd.DataFrame:
    """Eligibility for each formation date, given where its signal window starts."""
    pos = panel.calendar.get_indexer
    oob_cum = panel.out_of_band.astype(int).cumsum()
    listed = panel.close.notna().cumsum() > 0
    rows = []
    for f, w in zip(formation, window_start):
        i_f, i_w = pos([f])[0], pos([w])[0]
        start = max(i_w - TRADED_LOOKBACK, 0)
        clean = (oob_cum.iloc[i_f] - oob_cum.iloc[start]) == 0
        seasoned = listed.iloc[start]
        tradable = panel.traded_share.iloc[i_f] >= TRADED_SHARE_MIN
        priced = (panel.close_ffill.iloc[i_f].notna()
                  & panel.close_ffill.iloc[i_w].notna())
        rows.append(clean & seasoned & tradable & priced)
    return pd.DataFrame(rows, index=formation)


def trend_signals(panel: Panel) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """{name: (signal, eligible)}, each indexed by that signal's formation dates."""
    c = panel.close_ffill
    m = period_ends(panel.calendar, "M")
    w = period_ends(panel.calendar, "W")
    out = {}

    # momentum 12-1: needs month-ends t-12 and t-1
    f = m[12:]
    mom = pd.DataFrame(c.loc[m[11:-1]].to_numpy() / c.loc[m[:-12]].to_numpy() - 1,
                       index=f, columns=c.columns)
    out["momentum_12_1"] = (mom, _eligible(panel, f, m[:-12]))

    f = m[1:]
    rev_m = pd.DataFrame(c.loc[m[1:]].to_numpy() / c.loc[m[:-1]].to_numpy() - 1,
                         index=f, columns=c.columns)
    out["reversal_1m"] = (rev_m, _eligible(panel, f, m[:-1]))

    f = w[1:]
    rev_w = pd.DataFrame(c.loc[w[1:]].to_numpy() / c.loc[w[:-1]].to_numpy() - 1,
                         index=f, columns=c.columns)
    out["reversal_1w"] = (rev_w, _eligible(panel, f, w[:-1]))
    return out
