from quantforge.agents.expression_generator import ExpressionGeneratorAgent
from quantforge.agents.mathematical_critic import MathematicalCriticAgent


def test_deterministic_llm_expression_generator_for_offline_tests():
    agent = ExpressionGeneratorAgent(llm_provider="deterministic")
    expr = agent.generate(
        goal="Find mean reversion",
        mutation_instruction="Turnover is too high, smooth the signal",
        iteration=2,
        history=[],
        metrics={"turnover": 0.9},
    )
    assert "rank" in expr


def test_deterministic_llm_critic_for_offline_tests():
    critic = MathematicalCriticAgent(llm_provider="deterministic")
    msg = critic.critique(
        metrics={"sharpe": 0.2, "fitness": 0.1, "turnover": 0.8},
        expression="-rank(ts_rank(close, 5))",
        goal="Find mean reversion",
        history=["-rank(ts_rank(close, 5))"],
    )
    assert "Mutation instruction" in msg or "Smooth" in msg
