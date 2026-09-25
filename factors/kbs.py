"""Minimal client for KBS's public market-data endpoints.

Called directly rather than through a wrapper library: the common wrapper caps
unregistered callers at 20 requests per minute and truncates daily history to
eight years, neither of which the endpoints themselves impose. Politeness is
enforced here instead -- one request at a time, a minimum gap, backoff on errors.

Daily prices are adjusted by the provider for corporate actions: after each stock's
HOSE listing, moves beyond the 7% band between consecutive sessions are almost
absent, which unadjusted stock dividends would not allow. The adjustment method is
undocumented, and so is whether volume is restated to match. Adjusted close x
volume is therefore not treated as traded value anywhere downstream.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

BASE = "https://kbbuddywts.kbsec.com.vn/iis-server/investment"
MIN_GAP_S = 0.35
RETRIES = 3


class Kbs:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0.0.0 Safari/537.36"),
            "Accept": "application/json",
            "Referer": "https://kbbuddywts.kbsec.com.vn/",
        })
        self._last = 0.0

    def _get(self, url: str, params: dict | None = None):
        error = None
        for attempt in range(RETRIES):
            wait = MIN_GAP_S - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                r = self.session.get(url, params=params, timeout=30)
                if r.status_code == 200:
                    return r.json()
                error = RuntimeError(f"HTTP {r.status_code}")
            except (requests.RequestException, ValueError) as exc:
                error = exc
            time.sleep(2 ** attempt)
        raise RuntimeError(f"GET {url} failed after {RETRIES} attempts: {error}")

    def hose_symbols(self) -> list[str]:
        """Stocks currently listed on HOSE. Current only: see README, survivorship."""
        data = self._get(f"{BASE}/index/HOSE/stocks")
        symbols = data.get("data", []) if isinstance(data, dict) else data
        if len(symbols) < 300:
            raise RuntimeError(f"HOSE listing returned only {len(symbols)} symbols")
        return sorted(symbols)

    def profile(self, symbol: str) -> dict:
        """Listing date and exchange of the CURRENT listing, and current shares.

        For a stock that moved from UPCoM or HNX, the listing date is its HOSE
        date, which is what separates HOSE history from the earlier exchange.
        Shares outstanding is today's figure only.
        """
        d = self._get(f"{BASE}/stockinfo/profile/{symbol}")
        if isinstance(d, dict) and "data" in d and "LD" not in d:
            d = d["data"]
        if isinstance(d, list):
            d = d[0] if d else {}
        return {"symbol": symbol,
                "exchange": d.get("EX"),
                "listing_date": pd.to_datetime(d.get("LD"), format="%d/%m/%Y",
                                               errors="coerce"),
                "shares_outstanding_now": d.get("KLCPLH")}

    def daily_bars(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Adjusted daily OHLC and volume for a stock. Dates are DD-MM-YYYY."""
        return self._bars("stocks", symbol, start, end)

    def index_bars(self, code: str, start: str, end: str) -> pd.DataFrame:
        """Daily OHLC for an index, e.g. VNINDEX (a price index, no dividends)."""
        return self._bars("index", code, start, end)

    def _bars(self, root: str, symbol: str, start: str, end: str) -> pd.DataFrame:
        data = self._get(f"{BASE}/{root}/{symbol}/data_day",
                         params={"sdate": start, "edate": end})
        rows = data.get("data_day", []) if isinstance(data, dict) else []
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows).rename(columns={
            "t": "date", "o": "open", "h": "high", "l": "low", "c": "close",
            "v": "volume"})
        # Stamps arrive as "YYYY-MM-DD 07:00". Only the calendar date is meaningful;
        # comparing the raw stamp against midnight silently picks the prior session.
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        # The index endpoint mixes strings and numbers within a column.
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["symbol"] = symbol
        return df[["symbol", "date", "open", "high", "low", "close", "volume"]]
