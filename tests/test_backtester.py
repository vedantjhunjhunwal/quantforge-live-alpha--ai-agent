import pandas as pd
from quantforge.sandbox.backtester import VectorizedBacktestSandbox


def realish_df():
    idx = pd.date_range("2024-01-01", periods=80, tz="UTC")
    rows = []
    for symbol, offset in [("AAA", 100), ("BBB", 120), ("CCC", 90)]:
        for i, ts in enumerate(idx):
            close = offset + i * 0.1 + ((i % 5) - 2) * 0.05
            rows.append({"timestamp": ts, "symbol": symbol, "open": close - 0.1, "high": close + 0.2, "low": close - 0.2, "close": close, "volume": 1000 + i})
    return pd.DataFrame(rows)


def test_backtester_returns_metrics():
    sandbox = VectorizedBacktestSandbox(realish_df())
    metrics, diag = sandbox.run("-rank(decay_linear(ts_rank(close, 5), 10))")
    assert "sharpe" in metrics
    assert "fitness" in metrics
    assert "turnover" in metrics
    assert not diag.empty
