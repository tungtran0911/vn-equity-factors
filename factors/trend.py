"""Momentum and short-term reversal on HOSE: quintile sorts, after costs.

    python -m factors.trend

Prints every table in the README's trend section. All returns are per holding
period (a month or a week), equal-weighted, from the close one session after
formation to the close one session after the next formation.
"""

from __future__ import annotations

import sys

import pandas as pd

from factors.config import IN_SAMPLE_END
from factors.panel import load
from factors.report import (cost_section, pct, quintile_section, subperiod_section,
                            summary_section)
from factors.signals import trend_signals
from factors.sorts import N_QUANTILES, quintile_backtest
from factors.stats import newey_west

# (signal, quintile held long, quintile held short, periods per year)
STRATEGIES = {
    "momentum_12_1": (N_QUANTILES, 1, 12),
    "reversal_1m": (1, N_QUANTILES, 12),
    "reversal_1w": (1, N_QUANTILES, 52),
}


# Buckets of a stock's return on the day, and the label each is reported under.
# 6.5% is where a close sits at or next to the 7% limit once tick rounding is
# allowed for; moves beyond 7.5% are not HOSE moves and are excluded upstream.
MOVE_BUCKETS = [
    (0.065, 1.0, "at or near the ceiling (>= +6.5%)"),
    (0.03, 0.065, "+3% to +6.5%"),
    (-0.03, 0.03, "-3% to +3%"),
    (-0.065, -0.03, "-6.5% to -3%"),
    (-1.0, -0.065, "at or near the floor (<= -6.5%)"),
]


def next_session_after_formation(panel, signals) -> None:
    """Return of the extreme quintiles over the one session the sorts skip."""
    pos = panel.calendar.get_indexer
    c = panel.close_ffill
    print("\n## The skipped session: extreme quintiles vs the universe (%, t)\n")
    print("| signal | Q1 (losers) | Q5 (winners) |")
    print("|---|---|---|")
    for name in ("reversal_1w", "reversal_1m"):
        sig, elig = signals[name]
        rows = []
        for f in sig.index:
            i = pos([f])[0]
            if i + 1 >= len(panel.calendar):
                continue
            s = sig.loc[f][elig.loc[f]].dropna()
            r = (c.iloc[i + 1][s.index] / c.iloc[i][s.index] - 1).dropna()
            if len(r) < N_QUANTILES * 5:
                continue
            q = pd.qcut(s.loc[r.index].rank(method="first"), N_QUANTILES,
                        labels=range(1, N_QUANTILES + 1))
            rows.append({"Q1": r[q == 1].mean() - r.mean(),
                         "Q5": r[q == N_QUANTILES].mean() - r.mean()})
        d = pd.DataFrame(rows)
        cells = [f"{m * 100:+.3f} ({t:+.2f})"
                 for m, t in (newey_west(d["Q1"]), newey_west(d["Q5"]))]
        print(f"| {name} | " + " | ".join(cells) + " |")


def next_session_by_move(panel) -> None:
    """Next-session return, relative to that session's universe mean, by the size
    of today's move. Each day's bucket average is one observation; inference is
    Newey-West over days."""
    c = panel.close_ffill
    nxt = c.shift(-1) / c - 1
    excess = nxt.sub(nxt.mean(axis=1), axis=0)
    print("\n## Next-session return by today's move, relative to the universe\n")
    print("| today's close-to-close move | stock-days | next session (%) | t |")
    print("|---|---|---|---|")
    for lo, hi, label in MOVE_BUCKETS:
        mask = (panel.ret >= lo) & (panel.ret < hi) & ~panel.out_of_band
        m, t = newey_west(excess.where(mask).mean(axis=1).dropna())
        print(f"| {label} | {int(mask.to_numpy().sum()):,} | {m * 100:+.3f} | {t:+.2f} |")


def run() -> int:
    panel = load(end=IN_SAMPLE_END)
    signals = trend_signals(panel)
    results = {}

    for name in STRATEGIES:
        sig, elig = signals[name]
        results[name] = quintile_backtest(panel, sig, elig, skip=1)
        quintile_section(name, results[name])

    summary_section(results, STRATEGIES)
    cost_section(results, STRATEGIES)

    print("\n## Skip-day sensitivity: long - short, per period (t)\n")
    print("| strategy | enter at formation close | enter one session later |")
    print("|---|---|---|")
    for name, (long_q, short_q, _) in STRATEGIES.items():
        sig, elig = signals[name]
        cells = []
        for skip in (0, 1):
            bt = results[name] if skip == 1 else quintile_backtest(panel, sig, elig, 0)
            m, t = newey_west(bt[f"Q{long_q}"] - bt[f"Q{short_q}"])
            cells.append(f"{pct(m)} ({t:+.2f})")
        print(f"| {name} | " + " | ".join(cells) + " |")

    subperiod_section(results, STRATEGIES)

    next_session_after_formation(panel, signals)
    next_session_by_move(panel)
    return 0


if __name__ == "__main__":
    sys.exit(run())
