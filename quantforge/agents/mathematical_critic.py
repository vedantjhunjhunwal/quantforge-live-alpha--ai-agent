from __future__ import annotations

from typing import Dict, List, Optional

from quantforge.llm import LLMClient, LLMConfig, LLMResponseError


class MathematicalCriticAgent:
    """Node 4: LLM-powered quant critic.

    It never approves the alpha. It only diagnoses failure and emits mutation instructions.
    The deterministic Evaluation Gate remains the only pass/fail authority.
    """

    def __init__(self, llm_provider: str = "auto", llm_model: Optional[str] = None, allow_fallback: bool = True):
        self.llm = LLMClient(LLMConfig(provider=llm_provider, model=llm_model, allow_deterministic_fallback=allow_fallback))

    def critique(
        self,
        metrics: Dict[str, float],
        expression: str,
        goal: str,
        history: List[str],
    ) -> str:
        payload = self.llm.json_chat(
            self._system_prompt(),
            self._user_prompt(metrics, expression, goal, history),
        )
        instruction = str(payload.get("mutation_instruction", "")).strip()
        diagnosis = str(payload.get("diagnosis", "")).strip()
        if not instruction:
            raise LLMResponseError("Mathematical Critic LLM did not return a 'mutation_instruction' field.")
        return f"{diagnosis} Mutation instruction: {instruction}" if diagnosis else instruction

    @staticmethod
    def _system_prompt() -> str:
        return """
You are QuantForge Node 4: Mathematical Critic.
You are a quant research AI agent. You receive failed deterministic backtest metrics.
You must diagnose WHY the signal failed and produce one structural mutation instruction.
Return JSON only with this schema:
{"diagnosis": "<short diagnosis>", "mutation_instruction": "<specific instruction for the next expression>"}
Do not decide pass/fail. The deterministic Evaluation Gate already failed the alpha.
Prefer precise operator-level fixes using rank, ts_rank, ts_mean, decay_linear, zscore, delta, correlation.
""".strip()

    @staticmethod
    def _user_prompt(metrics: Dict[str, float], expression: str, goal: str, history: List[str]) -> str:
        return f"""
Goal: {goal}
Failed expression: {expression}
Metrics: {metrics}
Expression history: {history}
Gate thresholds: Sharpe >= 1.5, Fitness >= 1.0, Turnover <= 0.7.

Give one concrete mutation instruction.
Examples:
- If turnover is too high, smooth with decay_linear or longer ts_mean window.
- If Sharpe is negative, invert the expression direction.
- If fitness is weak, combine returns, close, and volume with different lookbacks.
- If expression repeats history, ask for a different operator combination.
Return JSON only.
""".strip()
