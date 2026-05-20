from quantforge.graph.workflow import QuantForgeWorkflow
from quantforge.graph.state import AlphaSignalState


def test_evaluation_gate_routes_pass():
    wf = QuantForgeWorkflow()
    state = AlphaSignalState(goal="x", provider="csv", symbols=["AAA"], llm_provider="deterministic")
    state.metrics = {"sharpe": 2.0, "fitness": 1.2, "turnover": 0.3}
    state = wf.evaluation_gate_node(state)
    assert state.decision == "export_validated_alpha"


def test_critic_node_sets_mutation():
    wf = QuantForgeWorkflow()
    state = AlphaSignalState(goal="x", provider="csv", symbols=["AAA"], llm_provider="deterministic")
    state.metrics = {"sharpe": 0.5, "fitness": 0.2, "turnover": 0.9}
    state = wf.mathematical_critic_node(state)
    assert "Mutation instruction" in state.mutation_instruction
