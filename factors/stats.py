"""Newey-West inference for a time series of portfolio returns."""

from __future__ import annotations

import numpy as np
import pandas as pd


def newey_west(x: pd.Series, lags: int | None = None) -> tuple[float, float]:
    """Mean and its Newey-West t-statistic.

    Portfolio returns are autocorrelated (momentum windows overlap in formation
    data; volatility clusters), so the i.i.d. standard error is too small. Lags
    default to floor(4 (T/100)^(2/9)), the usual automatic choice.
    """
    x = pd.Series(x).dropna().to_numpy(dtype=float)
    t = len(x)
    if t < 3:
        return float("nan"), float("nan")
    if lags is None:
        lags = int(np.floor(4 * (t / 100) ** (2 / 9)))
    e = x - x.mean()
    var = e @ e / t
    for k in range(1, lags + 1):
        w = 1 - k / (lags + 1)
        var += 2 * w * (e[k:] @ e[:-k]) / t
    se = np.sqrt(var / t)
    return float(x.mean()), float(x.mean() / se) if se > 0 else float("nan")
