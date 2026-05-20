from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from .expression_parser import evaluate_expression
from .metrics import sharpe_ratio, max_drawdown, fitness


class VectorizedBacktestSandbox:
    """Deterministic alpha backtest on real fetched market data."""

    def __init__(self, market_df: pd.DataFrame):
        self.market_df = market_df.copy()
        self.matrices = self._build_matrices(self.market_df)

    def _build_matrices(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        matrices = {}
        for field in ["open", "high", "low", "close", "volume"]:
            matrices[field] = df.pivot(index="timestamp", columns="symbol", values=field).sort_index().ffill()
        matrices["returns"] = matrices["close"].pct_change().fillna(0.0)
        return matrices

    def run(self, expression: str) -> Tuple[Dict[str, float], pd.DataFrame]:
        signal = evaluate_expression(expression, self.matrices)
        signal = signal.reindex_like(self.matrices["returns"]).replace([np.inf, -np.inf], 0).fillna(0.0)

        # Dollar-neutral cross-sectional portfolio from signal.
        demeaned = signal.sub(signal.mean(axis=1), axis=0)
        gross = demeaned.abs().sum(axis=1).replace(0, np.nan)
        weights = demeaned.div(gross, axis=0).fillna(0.0)

        # Avoid lookahead: today's signal trades next bar's return.
        future_returns = self.matrices["returns"].shift(-1).fillna(0.0)
        portfolio_returns = (weights * future_returns).sum(axis=1)

        turnover = weights.diff().abs().sum(axis=1).mean()
        sr = sharpe_ratio(portfolio_returns)
        mdd = max_drawdown(portfolio_returns)
        avg_ret = float(portfolio_returns.mean())
        fit = fitness(sr, avg_ret, float(turnover), mdd)

        metrics = {
            "sharpe": float(sr),
            "fitness": float(fit),
            "turnover": float(turnover),
            "avg_bar_return": avg_ret,
            "cumulative_return": float((1 + portfolio_returns).prod() - 1),
            "max_drawdown": float(mdd),
            "bars": float(len(portfolio_returns)),
        }
        diagnostics = pd.DataFrame({"portfolio_return": portfolio_returns, "equity": (1 + portfolio_returns).cumprod()})
        return metrics, diagnostics
