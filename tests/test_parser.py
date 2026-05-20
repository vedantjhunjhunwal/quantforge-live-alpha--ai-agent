import pandas as pd
from quantforge.sandbox.expression_parser import evaluate_expression, UnsafeExpressionError


def ctx():
    idx = pd.date_range("2024-01-01", periods=30, tz="UTC")
    cols = ["AAA", "BBB"]
    close = pd.DataFrame({"AAA": range(30), "BBB": range(30, 60)}, index=idx)
    volume = close * 100
    return {"open": close, "high": close, "low": close, "close": close, "volume": volume, "returns": close.pct_change().fillna(0)}


def test_safe_expression_runs():
    out = evaluate_expression("-rank(decay_linear(ts_rank(close, 5), 10))", ctx())
    assert out.shape == (30, 2)


def test_unsafe_expression_rejected():
    try:
        evaluate_expression("__import__('os').system('echo bad')", ctx())
        assert False
    except Exception as exc:
        assert isinstance(exc, UnsafeExpressionError)
