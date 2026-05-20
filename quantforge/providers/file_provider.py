from __future__ import annotations
import pandas as pd
from .base import MarketDataProvider, normalize_market_frame


class FileMarketDataProvider(MarketDataProvider):
    """Loads user-provided real CSV/parquet data. Does not generate data."""

    def __init__(self, path: str, kind: str):
        self.path = path
        self.kind = kind

    def fetch(self) -> pd.DataFrame:
        if self.kind == "csv":
            df = pd.read_csv(self.path)
        elif self.kind == "parquet":
            df = pd.read_parquet(self.path)
        else:
            raise ValueError(f"Unsupported file provider: {self.kind}")
        return normalize_market_frame(df)
