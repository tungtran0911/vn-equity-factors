"""Tests for the decisions a wrong result would hide inside.

    python -m pytest -q
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factors.panel import build
from factors.signals import period_ends, trend_signals
from factors.sorts import quintile_backtest, summarise
from factors.stats import newey_west


def test_out_of_band_ignores_trading_gaps():
    """+15% across three silent sessions is legal on HOSE; +10% in one is not."""
    dates = pd.bdate_range("2024-01-01", periods=4)
    close = pd.DataFrame({"A": [100, np.nan, np.nan, 115],
                          "B": [100, 110, 110, 110]}, index=dates, dtype=float)
    p = build(close, min_stocks=1)
    assert not p.out_of_band["A"].any()
    assert p.out_of_band.loc[dates[1], "B"]


def test_momentum_skips_the_most_recent_month_and_reversal_uses_it():
    """A stock flat for a year that doubles in the final month has zero 12-1
    momentum and +100% one-month reversal signal."""
    dates = pd.bdate_range("2023-01-02", "2024-02-29")
    price = pd.Series(100.0, index=dates)
    price[dates >= "2024-02-15"] = 200.0
    p = build(price.to_frame("A"), min_stocks=1)
    sig = trend_signals(p)
    last = sig["momentum_12_1"][0].index[-1]
    assert sig["momentum_12_1"][0].loc[last, "A"] == pytest.approx(0.0)
    assert sig["reversal_1m"][0].loc[last, "A"] == pytest.approx(1.0)


def test_unfinished_period_is_not_a_period_end():
    """Data ending on Thursday 2026-09-24 has no September month-end yet and no
    end for that week; data ending Friday has a complete week."""
    cal = pd.bdate_range("2026-08-03", "2026-09-24")
    assert period_ends(cal, "M")[-1] == pd.Timestamp("2026-08-31")
    assert period_ends(cal, "W")[-1] == pd.Timestamp("2026-09-18")
    cal = pd.bdate_range("2026-08-03", "2026-09-25")
    assert period_ends(cal, "W")[-1] == pd.Timestamp("2026-09-25")


def test_positions_enter_one_session_after_formation():
    """The top quintile jumps +10% the session after formation. Entering at the
    formation close would book that jump; entering one session later must not."""
    dates = pd.bdate_range("2024-01-01", periods=6)
    names = [f"S{i:02d}" for i in range(25)]
    close = pd.DataFrame(100.0, index=dates, columns=names)
    top = names[20:]
    close.loc[dates[1]:, top] = 110.0
    p = build(close, min_stocks=1)
    signal = pd.DataFrame([range(25), range(25)], index=[dates[0], dates[3]],
                          columns=names, dtype=float)
    eligible = signal.notna()
    later = quintile_backtest(p, signal, eligible, skip=1)
    same = quintile_backtest(p, signal, eligible, skip=0)
    assert later["Q5"].iloc[0] == pytest.approx(0.0)
    assert same["Q5"].iloc[0] == pytest.approx(0.10)


def test_costs_are_charged_to_the_long_leg_by_turnover():
    bt = pd.DataFrame({"Q1": [0.01, 0.02], "Q5": [0.03, 0.01],
                       "universe": [0.01, 0.01],
                       "turnover_Q1": [1.0, 0.5], "turnover_Q5": [1.0, 0.25]})
    s = summarise(bt, long_q=5, short_q=1, cost=0.004)
    assert s["long_excess_net"].tolist() == pytest.approx(
        [0.03 - 1.0 * 0.004 - 0.01, 0.01 - 0.25 * 0.004 - 0.01])
    assert s["long_short"].tolist() == pytest.approx([0.02, -0.01])


def test_newey_west_reduces_to_plain_t_without_lags():
    x = pd.Series([1.0, 2.0, 3.0, 4.0])
    mean, t = newey_west(x, lags=0)
    assert mean == pytest.approx(2.5)
    assert t == pytest.approx(2.5 / np.sqrt(1.25 / 4))


def test_dimson_beta_recovers_a_one_day_lagged_response():
    """A thinly traded stock that absorbs market news a day late has a same-day
    beta near zero and a Dimson beta near one."""
    from factors.risk import risk_signals
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2024-01-01", periods=320)
    market = pd.Series(rng.normal(0, 0.01, len(dates)), index=dates)
    stock = (1 + market.shift(1).fillna(0)).cumprod() * 100
    p = build(stock.to_frame("A"), min_stocks=1)
    rs = risk_signals(p, market=market)
    assert abs(rs["beta_ols"][0]["A"].iloc[-1]) < 0.15
    assert rs["beta_dimson"][0]["A"].iloc[-1] == pytest.approx(1.0, abs=0.05)


def test_capm_regression_recovers_alpha_and_beta():
    from factors.stats import capm_nw
    rng = np.random.default_rng(1)
    x = pd.Series(rng.normal(0.01, 0.05, 200))
    y = 0.004 + 1.5 * x + rng.normal(0, 0.001, 200)
    alpha, t, beta = capm_nw(y, x)
    assert alpha == pytest.approx(0.004, abs=0.0005)
    assert beta == pytest.approx(1.5, abs=0.01)
    assert t > 10


def test_fama_macbeth_recovers_the_cross_sectional_slope():
    from factors.stats import fama_macbeth
    rng = np.random.default_rng(2)
    dates = pd.date_range("2020-01-31", periods=24, freq="ME")
    x = pd.DataFrame(rng.uniform(0, 1, (24, 100)), index=dates)
    y = 2.0 * x + rng.normal(0, 0.1, (24, 100))
    slopes = fama_macbeth(y, {"x": x})
    assert len(slopes) == 24
    assert slopes["x"].mean() == pytest.approx(2.0, abs=0.02)
