from __future__ import annotations

from dataclasses import asdict, dataclass

from .llm import LLMAdapter, LLMMessage, LLMResponse


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class MatchedBudget:
    max_evidence_papers: int = 4
    max_total_tokens: int = 16000
    max_output_tokens_per_call: int = 700
    max_llm_calls: int = 8
    temperature: float = 0.0
    seed: int | None = 42


@dataclass
class BudgetUsage:
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMRuntime:
    """Per-architecture budget tracker around one shared LLM adapter."""

    def __init__(self, adapter: LLMAdapter, budget: MatchedBudget):
        self.adapter = adapter
        self.budget = budget
        self.usage = BudgetUsage()

    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        if self.usage.llm_calls >= self.budget.max_llm_calls:
            raise BudgetExceeded("LLM-call budget exhausted")

        estimated_input_tokens = self.adapter.count_tokens(messages)
        remaining = self.budget.max_total_tokens - self.usage.total_tokens
        # Real provider APIs may count protocol/message overhead differently from
        # local tokenizers. Reserve a small common margin when the adapter marks
        # preflight counts as estimates; provider-reported usage remains authoritative.
        reserve = 0 if self.adapter.token_count_is_exact else 256
        if estimated_input_tokens + reserve >= remaining:
            raise BudgetExceeded(
                "input would exceed total token budget: "
                f"estimated_input={estimated_input_tokens}, reserve={reserve}, remaining={remaining}"
            )

        max_output = min(
            self.budget.max_output_tokens_per_call,
            remaining - estimated_input_tokens - reserve,
        )
        if max_output <= 0:
            raise BudgetExceeded("no output-token budget remains")

        response = self.adapter.generate(
            messages,
            max_output_tokens=max_output,
            temperature=self.budget.temperature,
            seed=self.budget.seed,
        )

        if response.model_id != self.adapter.model_id:
            raise ValueError("adapter returned a response from a different model_id")
        if self.adapter.token_count_is_exact and response.usage.input_tokens != estimated_input_tokens:
            raise ValueError(
                "adapter token accounting mismatch: count_tokens and response usage disagree"
            )
        if response.usage.output_tokens > max_output:
            raise BudgetExceeded("adapter exceeded the allowed output-token budget")

        projected = self.usage.total_tokens + response.usage.total_tokens
        if projected > self.budget.max_total_tokens:
            raise BudgetExceeded("adapter response exceeded total token budget")

        self.usage.llm_calls += 1
        self.usage.input_tokens += response.usage.input_tokens
        self.usage.output_tokens += response.usage.output_tokens
        return response

    def metrics(self) -> dict:
        return {
            "model_id": self.adapter.model_id,
            "llm_calls": self.usage.llm_calls,
            "input_tokens": self.usage.input_tokens,
            "output_tokens": self.usage.output_tokens,
            "total_tokens": self.usage.total_tokens,
            "budget": asdict(self.budget),
        }
