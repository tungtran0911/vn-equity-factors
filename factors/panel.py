"""The daily price panel: HOSE-era history only, on the market calendar.

Three decisions live here because every factor inherits them:

  HOSE era only. Roughly a quarter of today's HOSE stocks traded on UPCoM
  (+/-15% band) or HNX (+/-10%) before transferring. That history is a different
  market with different limits, and it is where nearly all out-of-band daily
  moves sit. Each stock enters the panel on the day after its HOSE listing date;
  the listing day itself is dropped, since its return is measured against a
  price from another exchange.

  Market calendar. Days on which a stock did not trade are absent from the
  provider's data rather than recorded as zero volume, so tradability is measured
  against the market's calendar, not the stock's own rows.

  Stale prices. A holding-period return needs a price on the exit day. A stock
  that did not trade that day is valued at its last close, for at most five
  sessions; beyond that the position has no price and is dropped.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from factors.config import DAILY, OUT_OF_BAND, PROFILES, TRADED_LOOKBACK

MIN_STOCKS_FOR_A_TRADING_DAY = 100
STALE_LIMIT = 5


@dataclass
class Panel:
    close: pd.DataFrame        # date x symbol, NaN where no trade or pre-listing
    close_ffill: pd.DataFrame  # stale-valued close, for holding-period returns
    ret: pd.DataFrame          # daily simple return between consecutive traded days
    traded_share: pd.DataFrame # share of the last 60 market days with a trade
    out_of_band: pd.DataFrame  # bool: daily move beyond what the HOSE band allows
    calendar: pd.DatetimeIndex


def load(end: str | None = None) -> Panel:
    """HOSE-era panel through `end` (a date, inclusive), or through the last
    downloaded session."""
    daily = pd.read_parquet(DAILY)
    if end is not None:
        daily = daily[daily["date"] <= pd.Timestamp(end)]
    profiles = pd.read_parquet(PROFILES)[["symbol", "listing_date"]]
    daily = daily.merge(profiles, on="symbol", how="left")
    daily = daily[daily["date"] > daily["listing_date"]]
    close = daily.pivot(index="date", columns="symbol", values="close").sort_index()
    return build(close)


def build(close: pd.DataFrame,
          min_stocks: int = MIN_STOCKS_FOR_A_TRADING_DAY) -> Panel:
    """Derive the panel from a date x symbol frame of HOSE-era closes."""
    counts = close.notna().sum(axis=1)
    calendar = counts.index[counts >= min_stocks]
    close = close.reindex(calendar)

    traded = close.notna()
    traded_share = traded.rolling(TRADED_LOOKBACK, min_periods=TRADED_LOOKBACK).mean()

    # Return between consecutive traded days. Across a non-trading gap the move
    # accrued over several sessions and may legitimately exceed one day's band, so
    # the out-of-band test applies only when the previous session also traded.
    last = close.ffill()
    ret = close / last.shift(1) - 1
    ret = ret.where(traded)
    out_of_band = (ret.abs() > OUT_OF_BAND) & traded.shift(1, fill_value=False)

    return Panel(close=close,
                 close_ffill=close.ffill(limit=STALE_LIMIT),
                 ret=ret,
                 traded_share=traded_share,
                 out_of_band=out_of_band,
                 calendar=pd.DatetimeIndex(calendar))
