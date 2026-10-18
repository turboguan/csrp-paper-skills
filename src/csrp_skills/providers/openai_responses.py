from __future__ import annotations

import os
from typing import Sequence

from ..llm import LLMAdapter, LLMMessage, LLMResponse, LLMUsage


class OpenAIResponsesAdapter(LLMAdapter):
    """OpenAI Responses API adapter for the frozen Means Pilot model.

    The local tokenizer is used only for conservative preflight budgeting.
    Provider-reported usage in the Responses API result is authoritative.
    """

    token_count_is_exact = False

    def __init__(
        self,
        *,
        model_id: str = "gpt-6.1-sol",
        api_key: str | None = None,
        service_tier: str = "default",
    ):
        try:
            from openai import OpenAI
            import tiktoken
        except ImportError as exc:
            raise RuntimeError(
                "Install the OpenAI pilot extras with: pip install -e '.[openai]'"
            ) from exc

        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Store it as an environment variable or "
                "GitHub Actions secret; never commit an API key to the repository."
            )

        self.model_id = model_id
        self.service_tier = service_tier
        self._client = OpenAI(api_key=key)
        try:
            self._encoding = tiktoken.encoding_for_model(model_id)
        except KeyError:
            # Current OpenAI tokenizer guidance recommends tiktoken for
            # programmatic counting. This fallback is deliberately treated as
            # an estimate, never as authoritative billing usage.
            self._encoding = tiktoken.get_encoding("o200k_base")

    def count_tokens(self, messages: Sequence[LLMMessage]) -> int:
        # Conservative local estimate for preflight only. The protocol overhead
        # of Responses API messages can differ from the local tokenizer.
        total = 2
        for message in messages:
            total += 6
            total += len(self._encoding.encode(message.role))
            total += len(self._encoding.encode(message.content))
        return total

    def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        seed: int | None,
    ) -> LLMResponse:
        if seed is not None:
            raise ValueError(
                "The frozen OpenAI Responses pilot config uses seed=null. "
                "Do not silently introduce an unsupported sampling control."
            )

        response = self._client.responses.create(
            model=self.model_id,
            input=[
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            service_tier=self.service_tier,
            store=False,
        )

        response_model = str(response.model)
        usage = response.usage
        if usage is None:
            raise RuntimeError("OpenAI response did not include token usage.")

        return LLMResponse(
            text=response.output_text or "",
            usage=LLMUsage(
                input_tokens=int(usage.input_tokens),
                output_tokens=int(usage.output_tokens),
            ),
            model_id=response_model,
        )


def create_frozen_means_pilot_adapter() -> OpenAIResponsesAdapter:
    """Factory used by scripts/v06_means_pilot_real.py and GitHub Actions."""

    return OpenAIResponsesAdapter(
        model_id="gpt-6.1-sol",
        service_tier="default",
    )
