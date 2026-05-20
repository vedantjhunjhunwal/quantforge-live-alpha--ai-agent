from __future__ import annotations

import ast
from typing import Dict, List, Optional

from quantforge.llm import LLMClient, LLMConfig, LLMResponseError
from quantforge.sandbox.operators import ALLOWED_FIELDS, ALLOWED_OPERATORS


class ExpressionGeneratorAgent:
    """Node 1: LLM-powered alpha-expression generator.

    The LLM may propose expressions, but it is constrained to the project DSL.
    Unsafe expressions are rejected before they reach the sandbox.
    """

    def __init__(self, llm_provider: str = "auto", llm_model: Optional[str] = None, allow_fallback: bool = True):
        self.llm = LLMClient(LLMConfig(provider=llm_provider, model=llm_model, allow_deterministic_fallback=allow_fallback))

    def generate(
        self,
        goal: str,
        mutation_instruction: str,
        iteration: int,
        history: List[str],
        metrics: Optional[Dict[str, float]] = None,
    ) -> str:
        system_prompt = self._system_prompt()
        user_prompt = self._user_prompt(goal, mutation_instruction, iteration, history, metrics or {})
        payload = self.llm.json_chat(system_prompt, user_prompt)
        expression = str(payload.get("expression", "")).strip()
        if not expression:
            raise LLMResponseError("Expression Generator LLM did not return an 'expression' field.")
        self._validate_expression_syntax(expression)
        return expression

    @staticmethod
    def _system_prompt() -> str:
        ops = ", ".join(sorted(ALLOWED_OPERATORS.keys()))
        fields = ", ".join(sorted(ALLOWED_FIELDS))
        return f"""
You are QuantForge Node 1: Expression Generator.
You are an AI quant researcher generating ONE alpha formula for a deterministic sandbox.
Return JSON only with this schema:
{{"expression": "<alpha_expression>", "rationale": "<one sentence>"}}

Allowed fields: {fields}
Allowed operators: {ops}
Allowed math: +, -, *, /, parentheses, numeric constants.
Do not use Python code, imports, attributes, indexing, lambdas, assignments, comments, or prose in expression.
Expression must return a cross-sectional signal matrix.
Good examples:
-rank(decay_linear(ts_rank(close, 5), 10))
-rank(zscore(returns, 20))
rank(correlation(close, volume, 20))
-rank(ts_rank(volume, 10) + ts_rank(close, 5))
""".strip()

    @staticmethod
    def _user_prompt(
        goal: str,
        mutation_instruction: str,
        iteration: int,
        history: List[str],
        metrics: Dict[str, float],
    ) -> str:
        return f"""
User research goal: {goal}
Iteration: {iteration}
Mutation instruction from critic: {mutation_instruction or "None. Generate a first candidate."}
Previous failed expressions: {history or []}
Previous metrics: {metrics or {}}

Generate a new expression that is not in the failed history when possible.
If turnover was high, use smoothing such as decay_linear or ts_mean.
If Sharpe was negative, consider inverting the expression.
If fitness was weak, combine price/returns/volume signals.
Return JSON only.
""".strip()

    @staticmethod
    def _validate_expression_syntax(expression: str) -> None:
        tree = ast.parse(expression, mode="eval")
        allowed_names = set(ALLOWED_FIELDS) | set(ALLOWED_OPERATORS)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id not in allowed_names:
                raise LLMResponseError(f"LLM generated unknown symbol '{node.id}' in expression: {expression}")
            if isinstance(node, (ast.Attribute, ast.Subscript, ast.Lambda, ast.Dict, ast.List, ast.Tuple, ast.Import, ast.ImportFrom)):
                raise LLMResponseError(f"LLM generated unsafe syntax in expression: {expression}")
