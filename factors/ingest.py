"""Download adjusted daily bars for every current HOSE stock.

One request per symbol returns its whole history, so a full refresh is ~400
requests and a few minutes. Always a full refresh: adjusted prices are restated
backwards whenever a stock pays a stock dividend, so appending new days onto old
history would splice two different adjustment bases together.

    python -m factors.ingest
"""

from __future__ import annotations

import json
import sys
from datetime import date

import pandas as pd

from factors.config import DAILY, DATA, HISTORY_START, PROFILES, UNIVERSE
from factors.kbs import Kbs


def run() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    kbs = Kbs()
    symbols = kbs.hose_symbols()
    today = date.today()
    end = today.strftime("%d-%m-%Y")
    print(f"{len(symbols)} HOSE symbols, {HISTORY_START} to {end}")

    frames, profiles, failed = [], [], []
    for i, sym in enumerate(symbols, 1):
        try:
            df = kbs.daily_bars(sym, HISTORY_START, end)
            profiles.append(kbs.profile(sym))
        except RuntimeError as exc:
            failed.append(sym)
            print(f"  {sym}: {exc}")
            continue
        if not df.empty:
            frames.append(df)
        if i % 50 == 0:
            print(f"  {i}/{len(symbols)}")
    pd.DataFrame(profiles).to_parquet(PROFILES, index=False)

    daily = (pd.concat(frames, ignore_index=True)
               .drop_duplicates(["symbol", "date"])
               .sort_values(["symbol", "date"])
               .reset_index(drop=True))
    daily.to_parquet(DAILY, index=False)
    UNIVERSE.write_text(json.dumps(
        {"as_of": today.isoformat(), "exchange": "HOSE", "symbols": symbols,
         "failed": failed}, indent=1))
    print(f"wrote {DAILY.name}: {len(daily):,} rows, {daily['symbol'].nunique()} "
          f"symbols, {daily['date'].min().date()} to {daily['date'].max().date()}; "
          f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
