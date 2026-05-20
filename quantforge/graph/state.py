from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlphaSignalState(BaseModel):
    """Shared state passed through the QuantForge L4 graph."""

    goal: str
    provider: str
    symbols: List[str]
    data_file: Optional[str] = None
    period: str = "6mo"
    interval: str = "1d"
    timeframe: str = "5m"
    limit: int = 1000

    # LLM-agent configuration. Default auto uses real LLM when a key exists,
    # otherwise falls back to the original deterministic partial-agent nodes.
    llm_provider: str = "auto"
    llm_model: Optional[str] = None
    llm_fallback: str = "auto"  # auto or strict
    runtime_timestamp: Optional[str] = None

    current_expression: str = ""
    mutation_instruction: str = ""
    iteration: int = 0
    max_mutations: int = 5

    metrics: Dict[str, float] = Field(default_factory=dict)
    latest_timestamp: Optional[str] = None
    market_rows: int = 0
    is_signal_viable: bool = False
    decision: str = "pending"

    critique_history: List[str] = Field(default_factory=list)
    expression_history: List[str] = Field(default_factory=list)
    node_trace: List[str] = Field(default_factory=list)
    provider_metadata: Dict[str, Any] = Field(default_factory=dict)
