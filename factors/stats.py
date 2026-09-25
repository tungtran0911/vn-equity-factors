"""Newey-West inference and Fama-MacBeth cross-sectional regressions."""

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


def fama_macbeth(y: pd.DataFrame, regressors: dict[str, pd.DataFrame],
                 min_obs: int = 50) -> pd.DataFrame:
    """One cross-sectional OLS of y on the regressors (plus an intercept) per date.

    Returns the slopes, one row per date; their time-series mean with a
    Newey-West t-statistic is the Fama-MacBeth estimate. Dates with fewer than
    `min_obs` complete stocks are skipped.
    """
    names = list(regressors)
    rows = {}
    for d in y.index:
        df = pd.DataFrame({k: regressors[k].loc[d] for k in names})
        df["y"] = y.loc[d]
        df = df.dropna()
        if len(df) < min_obs:
            continue
        X = np.column_stack([np.ones(len(df)), df[names].to_numpy()])
        rows[d] = np.linalg.lstsq(X, df["y"].to_numpy(), rcond=None)[0][1:]
    return pd.DataFrame.from_dict(rows, orient="index", columns=names)


def capm_nw(y: pd.Series, x: pd.Series,
            lags: int | None = None) -> tuple[float, float, float]:
    """Intercept (alpha), its Newey-West t-statistic, and slope (beta) of y on x."""
    d = pd.concat([pd.Series(y), pd.Series(x)], axis=1).dropna().to_numpy(dtype=float)
    t = len(d)
    X = np.column_stack([np.ones(t), d[:, 1]])
    coef = np.linalg.lstsq(X, d[:, 0], rcond=None)[0]
    e = d[:, 0] - X @ coef
    if lags is None:
        lags = int(np.floor(4 * (t / 100) ** (2 / 9)))
    xe = X * e[:, None]
    s = xe.T @ xe
    for k in range(1, lags + 1):
        w = 1 - k / (lags + 1)
        g = xe[k:].T @ xe[:-k]
        s += w * (g + g.T)
    xtx_inv = np.linalg.inv(X.T @ X)
    cov = xtx_inv @ s @ xtx_inv
    return float(coef[0]), float(coef[0] / np.sqrt(cov[0, 0])), float(coef[1])


def deflated_sharpe(returns: pd.Series, trial_sharpes: list[float]
                    ) -> tuple[float, float, float]:
    """Deflated Sharpe ratio (Bailey and Lopez de Prado, 2014).

    The best of N backtests has a positive expected Sharpe ratio even when every
    strategy is worthless. The benchmark SR0 is that expected maximum, from the
    dispersion of the trials' Sharpe ratios; the deflated ratio is the probability
    that the selected strategy's true Sharpe exceeds it, given the sample length,
    skewness and kurtosis of its returns. Sharpe ratios are per period.

    Returns (sharpe, sr0, probability).
    """
    from statistics import NormalDist

    x = pd.Series(returns).dropna()
    t = len(x)
    sr = x.mean() / x.std(ddof=1)
    n = len(trial_sharpes)
    emc = 0.5772156649  # Euler-Mascheroni constant
    z = NormalDist()
    sr0 = float(np.std(trial_sharpes, ddof=1)) * (
        (1 - emc) * z.inv_cdf(1 - 1 / n) + emc * z.inv_cdf(1 - 1 / (n * np.e)))
    skew, kurt = x.skew(), x.kurt() + 3  # pandas kurt is excess kurtosis
    denom = np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    prob = z.cdf((sr - sr0) * np.sqrt(t - 1) / denom)
    return float(sr), float(sr0), float(prob)
