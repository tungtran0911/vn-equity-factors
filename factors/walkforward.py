"""Train / validation / test on the historical sample.

    python -m factors.walkforward

This is PSEUDO out-of-sample. The characteristics were chosen after studying
2017-2026 -- the limit-up count in particular was added after seeing how MAX behaves
-- so the test years are not unseen data for the design, only for the fitted
parameters. What this exercise does measure honestly is how much a model fitted on
one period retains in the next, and whether a flexible model beats a theory-driven
one once both are judged out of their training window. Genuinely unseen data starts
after the freeze (factors.freeze).

Splits are by formation date, with a one-month purge at each boundary: the label of
the last training month is the next month's return, which is the one-month signal
of the first validation month, so keeping it would let the two sets share
information.

  train       2017-04 to 2021-11
  validation  2022-01 to 2023-11
  test        2024-01 to 2026-07

Candidates, all scoring the same six characteristic ranks:

  linear   Fama-MacBeth coefficients estimated on the training months; the score is
           their weighted sum of ranks. Every weight is a theory's prediction.
  signs    one-month rank minus limit-up rank: the two effects that were significant
           and stable in-sample, equally weighted, nothing estimated.
  lgbm     gradient-boosted trees on the stacked training stock-months, target the
           within-month rank of next-month return; four hyperparameter settings,
           chosen on validation.

The model with the highest mean validation rank IC is selected before the test set
is scored. All candidates are then reported on test, so the selection can be
judged, not only the winner.
"""

from __future__ import annotations

import sys

import lightgbm as lgb
import numpy as np
import pandas as pd

from factors import cross_section
from factors.config import COST_ROUND_TRIP, IN_SAMPLE_END
from factors.cross_section import FEATURES, CrossSection
from factors.panel import load
from factors.report import pct
from factors.sorts import N_QUANTILES
from factors.stats import deflated_sharpe, fama_macbeth, newey_west

# By calendar month, not date: a month's last trading day moves with holidays
# (January 2022 ended on the 28th, before Tet), and a date cut-off would silently
# drop or add a month.
TRAIN_END = pd.Period("2021-11", "M")
VALID_START, VALID_END = pd.Period("2022-01", "M"), pd.Period("2023-11", "M")
TEST_START = pd.Period("2024-01", "M")
LGBM_GRID = [{"num_leaves": leaves, "n_estimators": trees}
             for leaves in (7, 15) for trees in (100, 300)]


def splits(cs: CrossSection) -> dict[str, pd.DatetimeIndex]:
    d = cs.hold.index
    m = d.to_period("M")
    return {"train": d[m <= TRAIN_END],
            "validation": d[(m >= VALID_START) & (m <= VALID_END)],
            "test": d[m >= TEST_START]}


def _features(cs: CrossSection, date) -> pd.DataFrame:
    return pd.DataFrame({k: cs.ranks[k].loc[date] for k in FEATURES}).dropna()


def fit_linear(cs: CrossSection, dates) -> dict[str, float]:
    slopes = fama_macbeth(cs.hold.loc[dates], {k: cs.ranks[k] for k in FEATURES})
    return slopes.mean().to_dict()


def score_linear(coef: dict[str, float], cs: CrossSection, dates) -> pd.DataFrame:
    return pd.DataFrame({d: sum(coef[k] * _features(cs, d)[k] for k in FEATURES)
                         for d in dates}).T


def score_signs(cs: CrossSection, dates) -> pd.DataFrame:
    return pd.DataFrame({d: _features(cs, d).eval("one_month - limit_up_days")
                         for d in dates}).T


def fit_lgbm(cs: CrossSection, dates, params: dict) -> lgb.LGBMRegressor:
    blocks = []
    for d in dates:
        x = _features(cs, d)
        y = cs.hold.loc[d, x.index].dropna()
        x = x.loc[y.index]
        x["target"] = y.rank(pct=True)
        blocks.append(x)
    data = pd.concat(blocks)
    model = lgb.LGBMRegressor(learning_rate=0.03, min_child_samples=100,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                              random_state=0, deterministic=True, force_row_wise=True,
                              n_jobs=1, verbose=-1, **params)
    return model.fit(data[list(FEATURES)], data["target"])


def score_lgbm(model, cs: CrossSection, dates) -> pd.DataFrame:
    out = {}
    for d in dates:
        x = _features(cs, d)
        out[d] = pd.Series(model.predict(x[list(FEATURES)]), index=x.index)
    return pd.DataFrame(out).T


def evaluate(scores: pd.DataFrame, cs: CrossSection,
             cost: float = COST_ROUND_TRIP) -> pd.DataFrame:
    """Per month: rank IC, and the top quintile's return over the universe of
    scored stocks, gross and net of turnover costs."""
    rows, previous = {}, None
    for d in scores.index:
        s = scores.loc[d].dropna()
        r = cs.hold.loc[d, s.index].dropna()
        s = s.loc[r.index]
        if len(s) < N_QUANTILES * 5:
            continue
        top = set(s.index[s.rank(method="first", pct=True) > 1 - 1 / N_QUANTILES])
        turnover = 1.0 if previous is None else len(top - previous) / len(top)
        previous = top
        gross = r.loc[list(top)].mean() - r.mean()
        rows[d] = {"ic": s.rank().corr(r.rank()), "gross": gross,
                   "net": gross - turnover * cost}
    return pd.DataFrame.from_dict(rows, orient="index")


def run() -> int:
    cs = cross_section.build(load(end=IN_SAMPLE_END))
    sets = splits(cs)
    print("## Splits (formation months)\n")
    for name, d in sets.items():
        print(f"- {name}: {d[0].date()} to {d[-1].date()}, {len(d)} months")

    coef = fit_linear(cs, sets["train"])
    print("\n## Linear model: Fama-MacBeth coefficients on the training months "
          "(% a month, lowest to highest rank)\n")
    print("| " + " | ".join(FEATURES) + " |")
    print("|---" * len(FEATURES) + "|")
    print("| " + " | ".join(pct(coef[k]) for k in FEATURES) + " |")

    candidates = {"linear": lambda d: score_linear(coef, cs, d),
                  "signs": lambda d: score_signs(cs, d)}
    for params in LGBM_GRID:
        model = fit_lgbm(cs, sets["train"], params)
        name = f"lgbm_{params['num_leaves']}l_{params['n_estimators']}t"
        candidates[name] = lambda d, m=model: score_lgbm(m, cs, d)

    results = {(name, split): evaluate(score(sets[split]), cs)
               for name, score in candidates.items()
               for split in ("validation", "test")}
    valid_ic = {name: results[(name, "validation")]["ic"].mean()
                for name in candidates}
    chosen = max(valid_ic, key=valid_ic.get)

    for split in ("validation", "test"):
        print(f"\n## {split.capitalize()}: per month (t)\n")
        print("| model | rank IC | IC > 0 | top quintile - universe, gross "
              "| net of costs |")
        print("|---|---|---|---|---|")
        for name in candidates:
            e = results[(name, split)]
            ic, t_ic = newey_west(e["ic"])
            g, t_g = newey_west(e["gross"])
            n, t_n = newey_west(e["net"])
            mark = " (selected)" if name == chosen else ""
            print(f"| {name}{mark} | {ic:+.3f} ({t_ic:+.2f}) | {(e['ic'] > 0).mean():.0%} "
                  f"| {pct(g)} ({t_g:+.2f}) | {pct(n)} ({t_n:+.2f}) |")

    trial_sr = [results[(n, "validation")]["net"].mean()
                / results[(n, "validation")]["net"].std(ddof=1) for n in candidates]
    sr, sr0, prob = deflated_sharpe(results[(chosen, "validation")]["net"], trial_sr)
    print(f"\n## Selection\n")
    print(f"selected on validation rank IC: {chosen}. Its validation Sharpe ratio of "
          f"net monthly excess returns is {sr:.3f}; the expected best of "
          f"{len(trial_sr)} worthless trials is {sr0:.3f}; deflated probability that "
          f"the selected Sharpe is real: {prob:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
