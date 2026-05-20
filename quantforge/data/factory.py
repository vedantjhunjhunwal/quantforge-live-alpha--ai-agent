from __future__ import annotations


def make_provider(name: str, symbols, data_file=None, period="6mo", interval="1d", timeframe="5m", limit=1000):
    name = name.lower()
    if name == "yahoo":
        from quantforge.providers.yahoo_provider import YahooFinanceProvider
        return YahooFinanceProvider(symbols=symbols, period=period, interval=interval)
    if name == "binance":
        from quantforge.providers.binance_provider import BinanceOHLCVProvider
        return BinanceOHLCVProvider(symbols=symbols, timeframe=timeframe, limit=limit)
    if name in {"csv", "parquet"}:
        from quantforge.providers.file_provider import FileMarketDataProvider
        if not data_file:
            raise ValueError("--data-file is required for csv/parquet provider")
        return FileMarketDataProvider(path=data_file, kind=name)
    raise ValueError(f"Unsupported provider: {name}")
