"""Quintile portfolio sorts with a skip day, name turnover and trading costs.

At each formation date the eligible stocks are ranked on the signal and split into
equal-weighted quintiles. Positions are entered at the close `skip` sessions after
formation and held until the close `skip` sessions after the next formation date.

The skip day is not a detail. Without it the signal and the entry share a closing
price, so a close that printed at the ask and reverts to the bid shows up as
"reversal" that no one could have traded; and on a band-limited market, orders left
unfilled at a limit spill into the next session, which also looks like a signal.
Both are reported with and without the skip for the reversal strategies.

Turnover is the share of a quintile's names that are new at each rebalance
(equal weights, drift ignored). The cost of a rebalance is turnover x round-trip
cost, charged to the long leg only: short selling is not permitted on HOSE, so the
short leg of a long-short spread is not a position anyone can hold.
"""

from __future__ import annotations

import pandas as pd

from factors.panel import Panel

N_QUANTILES = 5


def quintile_backtest(panel: Panel, signal: pd.DataFrame, eligible: pd.DataFrame,
                      skip: int = 1) -> pd.DataFrame:
    """One row per holding period: quintile returns Q1..Q5, the universe, and the
    one-way turnover of each quintile. Q1 holds the lowest signal values."""
    pos = panel.calendar.get_indexer
    formation = signal.index
    rows, previous = [], {}
    for f, f_next in zip(formation[:-1], formation[1:]):
        i_in, i_out = pos([f])[0] + skip, pos([f_next])[0] + skip
        if i_out >= len(panel.calendar):
            break
        entry, exit_ = panel.calendar[i_in], panel.calendar[i_out]
        s = signal.loc[f][eligible.loc[f]].dropna()
        p_in = panel.close_ffill.loc[entry, s.index]
        p_out = panel.close_ffill.loc[exit_, s.index]
        r = (p_out / p_in - 1).dropna()
        s = s.loc[r.index]
        if len(s) < N_QUANTILES * 5:
            continue
        q = pd.qcut(s.rank(method="first"), N_QUANTILES,
                    labels=range(1, N_QUANTILES + 1))
        row = {"formation": f, "entry": entry, "exit": exit_,
               "n": len(s), "universe": r.mean()}
        for k in range(1, N_QUANTILES + 1):
            names = set(q.index[q == k])
            row[f"Q{k}"] = r.loc[list(names)].mean()
            prev = previous.get(k)
            row[f"turnover_Q{k}"] = (1.0 if prev is None
                                     else len(names - prev) / len(names))
            previous[k] = names
        rows.append(row)
    return pd.DataFrame(rows).set_index("formation")


def summarise(bt: pd.DataFrame, long_q: int, short_q: int, cost: float) -> dict:
    """Long-short spread (gross) and long-only excess over the universe (net)."""
    ls = bt[f"Q{long_q}"] - bt[f"Q{short_q}"]
    long_net = bt[f"Q{long_q}"] - bt[f"turnover_Q{long_q}"] * cost
    return {"long_short": ls,
            "long_excess_gross": bt[f"Q{long_q}"] - bt["universe"],
            "long_excess_net": long_net - bt["universe"],
            "turnover_long": bt[f"turnover_Q{long_q}"].iloc[1:].mean()}
