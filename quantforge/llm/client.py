from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class LLMConfigurationError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


@dataclass
class LLMConfig:
    provider: str = "auto"
    model: Optional[str] = None
    temperature: float = 0.15
    max_tokens: int = 500
    allow_deterministic_fallback: bool = True


class LLMClient:
    """Small provider wrapper for LLM calls.

    Provider behavior:
    - auto: use OpenAI if OPENAI_API_KEY exists, else Gemini if GOOGLE_API_KEY/GEMINI_API_KEY exists,
      else fall back to deterministic agent nodes.
    - openai/gemini: use the selected provider; if the key is missing and fallback is enabled, use deterministic.
    - deterministic: original partial-agent mode with rule-based expression/critic nodes.
    
    Market data is never faked. Fallback only changes the LLM reasoning nodes.
    """

    def __init__(self, config: LLMConfig):
        load_dotenv()
        self.config = config
        self.provider = self._resolve_provider(config.provider.lower().strip())

    def _resolve_provider(self, requested: str) -> str:
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        has_gemini = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

        if requested == "auto":
            if has_openai:
                return "openai"
            if has_gemini:
                return "gemini"
            return "deterministic"

        if requested == "openai" and not has_openai and self.config.allow_deterministic_fallback:
            return "deterministic"
        if requested == "gemini" and not has_gemini and self.config.allow_deterministic_fallback:
            return "deterministic"

        return requested

    def json_chat(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if self.provider == "openai":
            return self._openai_json(system_prompt, user_prompt)
        if self.provider == "gemini":
            return self._gemini_json(system_prompt, user_prompt)
        if self.provider == "deterministic":
            return self._deterministic_json(system_prompt, user_prompt)
        raise LLMConfigurationError(
            f"Unsupported LLM provider '{self.provider}'. Use auto, openai, gemini, or deterministic."
        )

    def _openai_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is missing. Create a .env file from .env.example and add your key, "
                "or run with --llm-provider auto to fall back to deterministic agent nodes."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError("Install openai package: pip install openai") from exc

        model = self.config.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return self._parse_json(content)

    def _gemini_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "GOOGLE_API_KEY or GEMINI_API_KEY is missing. Create a .env file from .env.example "
                "and add your key, or run with --llm-provider auto to fall back to deterministic agent nodes."
            )
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise LLMConfigurationError("Install Gemini SDK: pip install google-generativeai") from exc

        model_name = self.config.model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
                "response_mime_type": "application/json",
            },
        )
        response = model.generate_content(user_prompt)
        return self._parse_json(response.text or "{}")

    def _deterministic_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        lower = user_prompt.lower()
        system_lower = system_prompt.lower()
        if "expression generator" in system_lower:
            if "turnover" in lower or "smooth" in lower:
                expr = "-rank(decay_linear(ts_rank(close, 10), 20))"
            elif "negative" in lower or "invert" in lower:
                expr = "rank(decay_linear(ts_rank(close, 10), 20))"
            else:
                expr = "-rank(decay_linear(zscore(returns, 20), 10))"
            return {"expression": expr, "rationale": "Deterministic offline expression for tests."}
        return {
            "diagnosis": "Offline deterministic critic: metrics failed the gate.",
            "mutation_instruction": "Smooth the signal using decay_linear and try a longer time-series window.",
        }

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # tolerate ```json fenced responses
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if not match:
                raise LLMResponseError(f"LLM did not return JSON: {content[:300]}")
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise LLMResponseError(f"LLM returned invalid JSON: {content[:300]}") from exc
