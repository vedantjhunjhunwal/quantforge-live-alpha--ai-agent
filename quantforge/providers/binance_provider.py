from __future__ import annotations
from typing import List
import pandas as pd
import ccxt
from .base import MarketDataProvider, normalize_market_frame


class BinanceOHLCVProvider(MarketDataProvider):
    """Fetches latest public Binance OHLCV candles through ccxt. No synthetic fallback."""

    def __init__(self, symbols: List[str], timeframe: str = "5m", limit: int = 1000):
        self.symbols = symbols
        self.timeframe = timeframe
        self.limit = limit
        self.exchange = ccxt.binance({"enableRateLimit": True})

    def fetch(self) -> pd.DataFrame:
        frames = []
        errors = []
        for symbol in self.symbols:
            try:
                rows = self.exchange.fetch_ohlcv(symbol, timeframe=self.timeframe, limit=self.limit)
                if not rows:
                    errors.append(f"{symbol}: no rows returned")
                    continue
                frames.append(pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"]).assign(symbol=symbol))
            except Exception as exc:
                errors.append(f"{symbol}: {exc}")
        if not frames:
            raise RuntimeError(
                "Binance live fetch failed. Production mode does not use fake data. "
                + "; ".join(errors)
            )
        df = pd.concat(frames, ignore_index=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return normalize_market_frame(df)
