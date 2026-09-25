"""Freeze the models and hypotheses before any post-freeze data exists.

    python -m factors.freeze

Writes preregistration/frozen.json and the fitted LightGBM model. Committing them
to git before the first out-of-sample month closes is what makes the later test
honest: the commit timestamp shows the model existed before the data that scores it,
and nothing in the frozen files can be adjusted to the outcome.

Choosing the frozen models with the whole history in view -- including the pseudo
test years -- is legitimate here, and is the point of freezing: the evaluation data
does not exist yet, so no choice made now can have been fitted to it.

Also computes the statistical power of the pre-registered tests. An effect estimated
on the same data it was discovered in is biased upward, so the power figures are an
upper bound.
"""

from __future__ import annotations

import hashlib
import json
import sys
from statistics import NormalDist

import lightgbm as lgb
import numpy as np
import pandas as pd

from factors import cross_section
from factors.config import COST_ROUND_TRIP, DAILY, ROOT
from factors.cross_section import FEATURES
from factors.panel import load
from factors.stats import fama_macbeth
from factors.walkforward import fit_lgbm

OUT = ROOT / "preregistration"
FROZEN = OUT / "frozen.json"
LGBM_FILE = OUT / "lgbm_15l_100t.txt"
LGBM_PARAMS = {"num_leaves": 15, "n_estimators": 100}   # selected on validation
# The first formation month whose holding period lies entirely after the freeze.
# August 2026's portfolio is held through September, and September data up to the
# 25th was already in hand when the models were frozen.
FIRST_OOS_MONTH = "2026-09"
LOOKS_MONTHS = (12, 24, 36, 60)
PRIMARY_LOOK_MONTHS = 60
ALPHA_ONE_SIDED = 0.05


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def power_table(slopes: pd.Series, sign: int) -> list[dict]:
    """Power of a one-sided test of the mean monthly slope, if the true effect equals
    the in-sample estimate. Newey-West corrections are ignored here; the slopes are
    close to serially uncorrelated."""
    z = NormalDist()
    effect, sd = sign * slopes.mean(), slopes.std(ddof=1)
    crit = z.inv_cdf(1 - ALPHA_ONE_SIDED)
    rows = []
    for n in LOOKS_MONTHS:
        expected_t = effect / sd * np.sqrt(n)
        rows.append({"months": n, "expected_t": round(float(expected_t), 2),
                     "power": round(float(1 - z.cdf(crit - expected_t)), 2)})
    return rows


def run() -> int:
    if FROZEN.exists():
        print(f"{FROZEN} already exists. The freeze happens once; rerunning it would "
              f"replace the frozen models with ones fitted to later data. Nothing done.")
        return 1
    OUT.mkdir(exist_ok=True)
    panel = load()
    cs = cross_section.build(panel)
    history = cs.hold.index                         # every month with an outcome
    slopes = fama_macbeth(cs.hold.loc[history], {k: cs.ranks[k] for k in FEATURES})

    model = fit_lgbm(cs, history, LGBM_PARAMS)
    model.booster_.save_model(str(LGBM_FILE))

    frozen = {
        "frozen_at": pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").isoformat(timespec="seconds"),
        "data_last_session": str(panel.calendar[-1].date()),
        "data_file_sha256": sha256(DAILY),
        "history_formation_months": [str(history[0].date()), str(history[-1].date()),
                                     len(history)],
        "first_out_of_sample_formation_month": FIRST_OOS_MONTH,
        "features": list(FEATURES),
        "hypotheses": {
            "H1": {"statement": "limit-up days carry a negative price",
                   "test": "Fama-MacBeth slope on limit_up_days rank, all six features",
                   "sign": -1,
                   "in_sample_mean": round(float(slopes["limit_up_days"].mean()), 5),
                   "power_if_in_sample_effect_is_true":
                       power_table(slopes["limit_up_days"], -1)},
            "H2": {"statement": "one-month returns continue",
                   "test": "Fama-MacBeth slope on one_month rank, all six features",
                   "sign": 1,
                   "in_sample_mean": round(float(slopes["one_month"].mean()), 5),
                   "power_if_in_sample_effect_is_true":
                       power_table(slopes["one_month"], 1)},
        },
        "strategies": {
            "primary_signs": {"score": "rank(one_month) - rank(limit_up_days)",
                              "portfolio": "top quintile, equal weight, long only",
                              "benchmark": "equal-weighted scored universe",
                              "cost_round_trip": COST_ROUND_TRIP},
            "secondary_lgbm": {"model_file": LGBM_FILE.name,
                               "model_sha256": sha256(LGBM_FILE),
                               "params": LGBM_PARAMS,
                               "fitted_on_formation_months": len(history),
                               "portfolio": "top quintile, equal weight, long only",
                               "cost_round_trip": COST_ROUND_TRIP},
        },
        "decision_rule": {
            "primary_look_months": PRIMARY_LOOK_MONTHS,
            "one_sided_alpha": ALPHA_ONE_SIDED,
            "interim_looks_months": [n for n in LOOKS_MONTHS if n != PRIMARY_LOOK_MONTHS],
            "interim_looks_are": "descriptive only; no hypothesis is accepted or "
                                 "rejected before the primary look",
        },
        "versions": {"pandas": pd.__version__, "numpy": np.__version__,
                     "lightgbm": lgb.__version__},
    }
    FROZEN.write_text(json.dumps(frozen, indent=2))

    print(f"frozen at {frozen['frozen_at']}; data through {frozen['data_last_session']}")
    print(f"history: {len(history)} formation months; first out-of-sample formation "
          f"month: {FIRST_OOS_MONTH}")
    for h in ("H1", "H2"):
        d = frozen["hypotheses"][h]
        print(f"\n{h}: {d['statement']} (in-sample mean slope "
              f"{d['in_sample_mean'] * 100:+.2f}% a month)")
        print("| months of new data | expected t | power, one-sided 5% |")
        print("|---|---|---|")
        for row in d["power_if_in_sample_effect_is_true"]:
            print(f"| {row['months']} | {row['expected_t']:+.2f} | {row['power']:.0%} |")
    print(f"\n{FROZEN.name} sha256 {sha256(FROZEN)}")
    print(f"{LGBM_FILE.name} sha256 {sha256(LGBM_FILE)}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
