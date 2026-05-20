from __future__ import annotations
import numpy as np
import pandas as pd


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = returns.dropna()
    if len(r) < 2 or r.std() == 0:
        return 0.0
    return float(np.sqrt(periods_per_year) * r.mean() / r.std())


def max_drawdown(returns: pd.Series) -> float:
    curve = (1 + returns.fillna(0)).cumprod()
    peak = curve.cummax()
    dd = curve / peak - 1
    return float(dd.min()) if len(dd) else 0.0


def fitness(sharpe: float, avg_return: float, turnover: float, drawdown: float) -> float:
    penalty = 1.0 + max(turnover, 0) + abs(min(drawdown, 0))
    return float((abs(sharpe) * max(avg_return, 0.0001) * 100.0) / penalty)
