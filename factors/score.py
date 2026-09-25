"""Score the frozen models on data that did not exist when they were frozen.

    python -m factors.ingest    # refresh the data first
    python -m factors.score

Only formation months from 2026-09 onward are scored, and only once their holding
period has ended. Each scored month is appended to results/oos_ledger.csv and never
rewritten: the universe is today's listing at each run, so a stock delisted later
would silently drop out of a recomputation. The ledger keeps what was measured when
it was first measurable.

Run it monthly, after the first session of each month. A late run still produces
the same numbers -- the models are frozen and deterministic -- but a run that is
months late is more exposed to delistings.
"""

from __future__ import annotations

import hashlib
import json
import sys

import lightgbm as lgb
import pandas as pd

from factors import cross_section
from factors.config import ROOT
from factors.cross_section import FEATURES
from factors.freeze import FROZEN, LGBM_FILE
from factors.panel import load
from factors.report import pct
from factors.stats import fama_macbeth, newey_west
from factors.walkforward import evaluate, score_lgbm, score_signs

LEDGER = ROOT / "results" / "oos_ledger.csv"


def oos_months(index: pd.DatetimeIndex, first_month: str) -> pd.DatetimeIndex:
    """Formation dates in or after the first out-of-sample month."""
    return index[index.to_period("M") >= pd.Period(first_month, "M")]


def append_to_ledger(path, fresh: pd.DataFrame) -> int:
    """Append the months not yet in the ledger; return how many were added.

    The file is only ever appended to, never rewritten, so every byte of a month
    already recorded stays exactly as it was first written. (Reading a CSV and
    writing it back is not safe: float parsing alone changes trailing digits.)
    """
    if path.exists():
        recorded = pd.read_csv(path, usecols=["formation"],
                               parse_dates=["formation"])["formation"]
        fresh = fresh.loc[~fresh.index.isin(recorded)]
    if len(fresh):
        path.parent.mkdir(exist_ok=True)
        fresh.to_csv(path, mode="a", header=not path.exists())
    return len(fresh)


def run() -> int:
    frozen = json.loads(FROZEN.read_text())
    recorded = frozen["strategies"]["secondary_lgbm"]["model_sha256"]
    if hashlib.sha256(LGBM_FILE.read_bytes()).hexdigest() != recorded:
        print("the LightGBM file does not match the frozen hash; refusing to score")
        return 2
    model = lgb.Booster(model_file=str(LGBM_FILE))

    cs = cross_section.build(load())
    months = oos_months(cs.hold.index, frozen["first_out_of_sample_formation_month"])

    if len(months):
        slopes = fama_macbeth(cs.hold.loc[months], {k: cs.ranks[k] for k in FEATURES})
        signs = evaluate(score_signs(cs, months), cs)
        ml = evaluate(score_lgbm(model, cs, months), cs)
        fresh = pd.DataFrame({
            "h1_limit_up_slope": slopes["limit_up_days"],
            "h2_one_month_slope": slopes["one_month"],
            "signs_ic": signs["ic"], "signs_gross": signs["gross"],
            "signs_net": signs["net"],
            "lgbm_ic": ml["ic"], "lgbm_gross": ml["gross"], "lgbm_net": ml["net"],
        })
        fresh.index.name = "formation"
        fresh["scored_at"] = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").isoformat(
            timespec="seconds")
        append_to_ledger(LEDGER, fresh)

    ledger = (pd.read_csv(LEDGER, index_col="formation", parse_dates=["formation"],
                          float_precision="round_trip")
              if LEDGER.exists() else pd.DataFrame())
    rule = frozen["decision_rule"]
    n = len(ledger)
    print(f"out-of-sample months scored: {n} of {rule['primary_look_months']} "
          f"for the primary look (frozen {frozen['frozen_at']})")
    if n == 0:
        print(f"nothing to score yet: the first out-of-sample portfolio is formed at "
              f"the end of {frozen['first_out_of_sample_formation_month']} and its "
              f"holding period ends one session into the second month after it")
        return 0

    status = ("PRIMARY LOOK" if n >= rule["primary_look_months"]
              else "interim, descriptive only")
    print(f"status: {status}\n")
    print("| quantity | mean per month | t | months |")
    print("|---|---|---|---|")
    for col in ledger.columns.drop("scored_at"):
        m, t = newey_west(ledger[col])
        value = f"{m:+.3f}" if col.endswith("_ic") else pct(m)
        print(f"| {col} | {value} | {t:+.2f} | {ledger[col].notna().sum()} |")
    return 0


if __name__ == "__main__":
    sys.exit(run())
