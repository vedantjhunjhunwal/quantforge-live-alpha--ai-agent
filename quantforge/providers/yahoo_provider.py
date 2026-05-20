from __future__ import annotations
from typing import List
import pandas as pd
import yfinance as yf
from .base import MarketDataProvider, normalize_market_frame


class YahooFinanceProvider(MarketDataProvider):
    """Fetches latest available Yahoo Finance OHLCV bars. No synthetic fallback."""

    def __init__(self, symbols: List[str], period: str = "6mo", interval: str = "1d"):
        self.symbols = symbols
        self.period = period
        self.interval = interval

    def fetch(self) -> pd.DataFrame:
        frames = []
        errors = []
        for symbol in self.symbols:
            try:
                df = yf.download(
                    tickers=symbol,
                    period=self.period,
                    interval=self.interval,
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )
                if df is None or df.empty:
                    errors.append(f"{symbol}: no rows returned")
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0].lower() for c in df.columns]
                else:
                    df.columns = [str(c).lower() for c in df.columns]
                df = df.reset_index()
                time_col = "datetime" if "datetime" in df.columns else "date"
                frames.append(pd.DataFrame({
                    "timestamp": df[time_col],
                    "symbol": symbol,
                    "open": df["open"],
                    "high": df["high"],
                    "low": df["low"],
                    "close": df["close"],
                    "volume": df["volume"],
                }))
            except Exception as exc:
                errors.append(f"{symbol}: {exc}")
        if not frames:
            raise RuntimeError(
                "Yahoo Finance live fetch failed. Production mode does not use fake data. "
                + "; ".join(errors)
            )
        return normalize_market_frame(pd.concat(frames, ignore_index=True))
