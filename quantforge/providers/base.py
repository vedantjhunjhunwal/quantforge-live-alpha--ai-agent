from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import pandas as pd

REQUIRED_COLUMNS = ["timestamp", "symbol", "open", "high", "low", "close", "volume"]


class MarketDataProvider(ABC):
    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Return real market data as timestamp,symbol,open,high,low,close,volume."""


def normalize_market_frame(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Market data missing required columns: {missing}")

    out = df[REQUIRED_COLUMNS].copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    for c in ["open", "high", "low", "close", "volume"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=REQUIRED_COLUMNS)
    out = out.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    if out.empty:
        raise ValueError("Fetched market data is empty after validation.")
    return out
