from __future__ import annotations
from datetime import datetime, timezone
from typing import Literal

from quantforge.graph.state import AlphaSignalState
from quantforge.data.factory import make_provider
from quantforge.sandbox.backtester import VectorizedBacktestSandbox
from quantforge.agents.expression_generator import ExpressionGeneratorAgent
from quantforge.agents.mathematical_critic import MathematicalCriticAgent
from quantforge.exporter.alpha_exporter import AlphaExporter


class QuantForgeWorkflow:
    """Exact full AI-agent architecture implementation.

    Node 1: Expression Generator        -> LLM / prompt node
    Node 2: Backtest Sandbox            -> deterministic Pandas/NumPy engine
    Node 3: Evaluation Gate             -> deterministic router
    Node 4: Mathematical Critic         -> LLM / strategy node
    Pass: Export Validated Alpha
    """

    def __init__(self):
        self.exporter = AlphaExporter()

    def expression_generator_node(self, state: AlphaSignalState) -> AlphaSignalState:
        state.node_trace.append("NODE 1: Expression Generator (LLM)")
        state.iteration += 1
        generator = ExpressionGeneratorAgent(
            llm_provider=state.llm_provider,
            llm_model=state.llm_model,
            allow_fallback=(state.llm_fallback == "auto"),
        )
        expr = generator.generate(
            goal=state.goal,
            mutation_instruction=state.mutation_instruction,
            iteration=state.iteration,
            history=state.expression_history,
            metrics=state.metrics,
        )
        state.current_expression = expr
        state.expression_history.append(expr)
        return state

    def backtest_sandbox_node(self, state: AlphaSignalState) -> AlphaSignalState:
        state.node_trace.append("NODE 2: Backtest Sandbox (Deterministic)")
        state.runtime_timestamp = datetime.now(timezone.utc).isoformat()
        provider = make_provider(
            name=state.provider,
            symbols=state.symbols,
            data_file=state.data_file,
            period=state.period,
            interval=state.interval,
            timeframe=state.timeframe,
            limit=state.limit,
        )
        market_df = provider.fetch()
        state.market_rows = len(market_df)
        state.latest_timestamp = str(market_df["timestamp"].max())
        state.provider_metadata = {
            "provider": state.provider,
            "symbols": state.symbols,
            "rows": len(market_df),
            "runtime_timestamp_utc": state.runtime_timestamp,
            "latest_market_timestamp": state.latest_timestamp,
            "llm_provider_requested": state.llm_provider,
            "llm_model": state.llm_model,
            "llm_fallback": state.llm_fallback,
        }
        sandbox = VectorizedBacktestSandbox(market_df)
        metrics, _diagnostics = sandbox.run(state.current_expression)
        state.metrics = metrics
        return state

    def evaluation_gate_node(self, state: AlphaSignalState) -> AlphaSignalState:
        state.node_trace.append("NODE 3: Evaluation Gate (Deterministic Router)")
        sharpe = state.metrics.get("sharpe", 0.0)
        fitness = state.metrics.get("fitness", 0.0)
        turnover = state.metrics.get("turnover", 999.0)
        if sharpe >= 1.5 and fitness >= 1.0 and turnover <= 0.7:
            state.is_signal_viable = True
            state.decision = "export_validated_alpha"
        elif state.iteration >= state.max_mutations:
            state.is_signal_viable = False
            state.decision = "discard_hypothesis_max_mutations"
        else:
            state.is_signal_viable = False
            state.decision = "send_to_mathematical_critic"
        return state

    def mathematical_critic_node(self, state: AlphaSignalState) -> AlphaSignalState:
        state.node_trace.append("NODE 4: Mathematical Critic (LLM)")
        critic = MathematicalCriticAgent(
            llm_provider=state.llm_provider,
            llm_model=state.llm_model,
            allow_fallback=(state.llm_fallback == "auto"),
        )
        critique = critic.critique(
            metrics=state.metrics,
            expression=state.current_expression,
            goal=state.goal,
            history=state.expression_history,
        )
        state.critique_history.append(critique)
        state.mutation_instruction = critique
        return state

    def export_node(self, state: AlphaSignalState) -> AlphaSignalState:
        state.node_trace.append("EXPORT: Validated Alpha")
        payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "goal": state.goal,
            "expression": state.current_expression,
            "metrics": state.metrics,
            "runtime_timestamp_utc": state.runtime_timestamp,
            "latest_market_timestamp": state.latest_timestamp,
            "provider_metadata": state.provider_metadata,
            "llm_provider_requested": state.llm_provider,
            "llm_model": state.llm_model,
            "llm_fallback": state.llm_fallback,
            "iterations": state.iteration,
            "critique_history": state.critique_history,
            "expression_history": state.expression_history,
            "node_trace": state.node_trace,
        }
        path = self.exporter.export(payload)
        state.provider_metadata["export_path"] = str(path)
        return state

    def route_after_gate(self, state: AlphaSignalState) -> Literal["export", "critic", "end"]:
        if state.decision == "export_validated_alpha":
            return "export"
        if state.decision == "send_to_mathematical_critic":
            return "critic"
        return "end"

    def run_fallback_graph(self, state: AlphaSignalState) -> AlphaSignalState:
        """Same node order as LangGraph. No fake market data.

        If llm_fallback='auto', only the LLM nodes may fall back to deterministic behavior
        when API keys are absent; live/vendor market data still must be real.
        """
        while True:
            state = self.expression_generator_node(state)
            state = self.backtest_sandbox_node(state)
            state = self.evaluation_gate_node(state)
            route = self.route_after_gate(state)
            if route == "export":
                return self.export_node(state)
            if route == "critic":
                state = self.mathematical_critic_node(state)
                continue
            return state

    def run(self, state: AlphaSignalState) -> AlphaSignalState:
        try:
            from langgraph.graph import END, StateGraph
        except Exception:
            return self.run_fallback_graph(state)

        graph = StateGraph(AlphaSignalState)
        graph.add_node("expression_generator", self.expression_generator_node)
        graph.add_node("backtest_sandbox", self.backtest_sandbox_node)
        graph.add_node("evaluation_gate", self.evaluation_gate_node)
        graph.add_node("mathematical_critic", self.mathematical_critic_node)
        graph.add_node("export_validated_alpha", self.export_node)

        graph.set_entry_point("expression_generator")
        graph.add_edge("expression_generator", "backtest_sandbox")
        graph.add_edge("backtest_sandbox", "evaluation_gate")
        graph.add_conditional_edges(
            "evaluation_gate",
            self.route_after_gate,
            {"export": "export_validated_alpha", "critic": "mathematical_critic", "end": END},
        )
        graph.add_edge("mathematical_critic", "expression_generator")
        graph.add_edge("export_validated_alpha", END)
        app = graph.compile()
        result = app.invoke(state)
        return AlphaSignalState.model_validate(result)
