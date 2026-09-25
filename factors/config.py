"""Paths, market rules and the assumptions every result depends on.

Market rules are facts. The cost figure is an assumption and is reported with a
sensitivity range wherever it is used.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DAILY = DATA / "daily.parquet"
PROFILES = DATA / "profiles.parquet"
MARKET = DATA / "vnindex.parquet"
UNIVERSE = DATA / "universe.json"

HISTORY_START = "01-01-2016"      # DD-MM-YYYY, the provider's format

# HOSE daily price limit is +/-7% of the reference (previous close). A larger daily
# move on HOSE is impossible except on a listing's first day or after a long
# suspension, so it marks history from another exchange (HNX +/-10%, UPCoM +/-15%)
# or a corporate-action artifact. 7.5% leaves room for tick rounding.
BAND = 0.07
OUT_OF_BAND = 0.075

# Round-trip trading cost for a retail-sized order, as a fraction of value:
# brokerage of about 0.15% per side plus 0.1% personal income tax on the sell side.
# Brokerage varies by broker (roughly 0.1% to 0.35%), hence the sensitivity grid.
COST_ROUND_TRIP = 0.004
COST_GRID = (0.002, 0.004, 0.006)

# Annual risk-free rate for CAPM alphas. The data has no Vietnamese short-rate
# series; 12-month deposit and policy rates sat roughly between 4% and 6% over
# 2017-2026. A zero-cost long-short spread depends on it only through the market
# premium, so alphas are shown across the grid rather than at one value.
RISK_FREE_GRID = (0.0, 0.04, 0.06)
RISK_FREE = 0.04

# A stock is eligible at a formation date only if it traded on at least this share
# of the preceding 60 sessions. Adjustment-invariant, unlike any value threshold.
TRADED_SHARE_MIN = 0.95
TRADED_LOOKBACK = 60
