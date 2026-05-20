from __future__ import annotations
import numpy as np
import pandas as pd


def _rank_series(s: pd.Series) -> pd.Series:
    return s.rank(pct=True).fillna(0.0)


def rank(x: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Cross-sectional percentile rank by timestamp."""
    if isinstance(x, pd.DataFrame):
        return x.rank(axis=1, pct=True).fillna(0.0)
    return _rank_series(x)


def zscore(x: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    mu = x.rolling(window).mean()
    sd = x.rolling(window).std().replace(0, np.nan)
    return ((x - mu) / sd).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def ts_rank(x: pd.DataFrame, window: int) -> pd.DataFrame:
    return x.rolling(window).apply(lambda a: pd.Series(a).rank(pct=True).iloc[-1], raw=False).fillna(0.0)


def ts_mean(x: pd.DataFrame, window: int) -> pd.DataFrame:
    return x.rolling(window).mean().fillna(0.0)


def ts_std_dev(x: pd.DataFrame, window: int) -> pd.DataFrame:
    return x.rolling(window).std().fillna(0.0)


def delta(x: pd.DataFrame, window: int) -> pd.DataFrame:
    return x.diff(window).fillna(0.0)


def decay_linear(x: pd.DataFrame, window: int) -> pd.DataFrame:
    weights = np.arange(1, window + 1, dtype=float)
    weights /= weights.sum()
    return x.rolling(window).apply(lambda a: float(np.dot(a, weights)), raw=True).fillna(0.0)


def correlation(x: pd.DataFrame, y: pd.DataFrame, window: int) -> pd.DataFrame:
    return x.rolling(window).corr(y).replace([np.inf, -np.inf], np.nan).fillna(0.0)


ALLOWED_OPERATORS = {
    "rank": rank,
    "zscore": zscore,
    "ts_rank": ts_rank,
    "ts_mean": ts_mean,
    "ts_std_dev": ts_std_dev,
    "delta": delta,
    "decay_linear": decay_linear,
    "correlation": correlation,
}

ALLOWED_FIELDS = {"open", "high", "low", "close", "volume", "returns"}
