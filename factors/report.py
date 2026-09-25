"""Markdown tables shared by the studies, so every family is reported the same way.

`strategies` maps a signal name to (long quintile, short quintile, periods per
year). The long quintile is the one the strategy's premise says to buy.
"""

from __future__ import annotations

import pandas as pd

from factors.config import COST_GRID, COST_ROUND_TRIP
from factors.sorts import N_QUANTILES, summarise
from factors.stats import newey_west

Q = range(1, N_QUANTILES + 1)


def pct(x: float) -> str:
    return f"{x * 100:+.2f}"


def quintile_section(name: str, bt: pd.DataFrame,
                     extra_rows: dict[str, list[str]] | None = None) -> None:
    print(f"\n## {name}: {bt.index.min().date()} to {bt.index.max().date()}, "
          f"{len(bt)} periods, {bt['n'].mean():.0f} stocks per formation on "
          f"average (min {bt['n'].min()}, max {bt['n'].max()})\n")
    print("| | " + " | ".join(f"Q{k}" for k in Q) + " | universe |")
    print("|---" * (N_QUANTILES + 2) + "|")
    print("| mean return per period (%) | "
          + " | ".join(pct(bt[f"Q{k}"].mean()) for k in Q)
          + f" | {pct(bt['universe'].mean())} |")
    print("| mean turnover (names) | "
          + " | ".join(f"{bt[f'turnover_Q{k}'].iloc[1:].mean():.0%}" for k in Q)
          + " | |")
    for label, cells in (extra_rows or {}).items():
        print(f"| {label} | " + " | ".join(cells) + " | |")


def summary_section(results: dict[str, pd.DataFrame], strategies: dict) -> None:
    print("\n## Summary (per period; long leg = the quintile a long-only investor "
          f"would hold; costs charged to the long leg at {COST_ROUND_TRIP:.1%} "
          "round trip)\n")
    print("| strategy | long - short | t | annualised | long - universe, gross "
          "| t | long - universe, net | t | long turnover |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name, (long_q, short_q, per_year) in strategies.items():
        s = summarise(results[name], long_q, short_q, COST_ROUND_TRIP)
        ls, t_ls = newey_west(s["long_short"])
        g, t_g = newey_west(s["long_excess_gross"])
        n, t_n = newey_west(s["long_excess_net"])
        print(f"| {name} | {pct(ls)} | {t_ls:+.2f} | {pct(ls * per_year)} "
              f"| {pct(g)} | {t_g:+.2f} | {pct(n)} | {t_n:+.2f} "
              f"| {s['turnover_long']:.0%} |")


def cost_section(results: dict[str, pd.DataFrame], strategies: dict) -> None:
    print("\n## Cost sensitivity: long - universe, net, per period (t)\n")
    print("| strategy | " + " | ".join(f"{c:.1%} round trip" for c in COST_GRID) + " |")
    print("|---" * (len(COST_GRID) + 1) + "|")
    for name, (long_q, short_q, _) in strategies.items():
        cells = []
        for c in COST_GRID:
            m, t = newey_west(summarise(results[name], long_q, short_q, c)
                              ["long_excess_net"])
            cells.append(f"{pct(m)} ({t:+.2f})")
        print(f"| {name} | " + " | ".join(cells) + " |")


def subperiod_section(results: dict[str, pd.DataFrame], strategies: dict) -> None:
    print("\n## Subperiods: long - short, per period (t)\n")
    print("| strategy | first half | second half | split date |")
    print("|---|---|---|---|")
    for name, (long_q, short_q, _) in strategies.items():
        ls = summarise(results[name], long_q, short_q, COST_ROUND_TRIP)["long_short"]
        half = len(ls) // 2
        a, ta = newey_west(ls.iloc[:half])
        b, tb = newey_west(ls.iloc[half:])
        print(f"| {name} | {pct(a)} ({ta:+.2f}) | {pct(b)} ({tb:+.2f}) "
              f"| {ls.index[half].date()} |")
