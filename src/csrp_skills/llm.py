from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Sequence


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: LLMUsage
    model_id: str


class LLMAdapter(ABC):
    """Provider-neutral adapter used identically by every organization.

    A real provider adapter must implement token counting and generation for one
    fixed model/version. The same adapter instance is injected into all
    architectures in a matched experiment.
    """

    model_id: str

    @abstractmethod
    def count_tokens(self, messages: Sequence[LLMMessage]) -> int:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        seed: int | None,
    ) -> LLMResponse:
        raise NotImplementedError


class CallableLLMAdapter(LLMAdapter):
    """Thin adapter for plugging in any external LLM client without SDK lock-in.

    generate_fn must return either LLMResponse or a tuple:
        (text, input_tokens, output_tokens)

    count_tokens_fn must use the tokenizer for the same model whenever possible.
    """

    def __init__(
        self,
        *,
        model_id: str,
        generate_fn: Callable[..., LLMResponse | tuple[str, int, int]],
        count_tokens_fn: Callable[[Sequence[LLMMessage]], int],
    ):
        self.model_id = model_id
        self._generate_fn = generate_fn
        self._count_tokens_fn = count_tokens_fn

    def count_tokens(self, messages: Sequence[LLMMessage]) -> int:
        return int(self._count_tokens_fn(messages))

    def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        seed: int | None,
    ) -> LLMResponse:
        out = self._generate_fn(
            messages=messages,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            seed=seed,
            model_id=self.model_id,
        )
        if isinstance(out, LLMResponse):
            return out
        text, input_tokens, output_tokens = out
        return LLMResponse(
            text=str(text),
            usage=LLMUsage(int(input_tokens), int(output_tokens)),
            model_id=self.model_id,
        )


class DeterministicTestLLMAdapter(LLMAdapter):
    """Offline adapter for CI only; never report its output as model performance."""

    model_id = "deterministic-test-adapter"

    def __init__(self):
        self.calls: list[dict] = []

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [token for token in text.replace("\n", " ").split(" ") if token]

    def count_tokens(self, messages: Sequence[LLMMessage]) -> int:
        return sum(len(self._tokens(message.content)) + 1 for message in messages)

    def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        max_output_tokens: int,
        temperature: float,
        seed: int | None,
    ) -> LLMResponse:
        input_tokens = self.count_tokens(messages)
        joined = "\n".join(message.content for message in messages)
        claim_ids = []
        for token in joined.replace("[", " [").replace("]", "] ").split():
            cleaned = token.strip("[](),.;:")
            if "-C" in cleaned and cleaned not in claim_ids:
                claim_ids.append(cleaned)
        answer = "Test synthesis"
        if claim_ids:
            answer += " using " + " ".join(f"[{claim_id}]" for claim_id in claim_ids[:4])
        output_tokens = min(max_output_tokens, max(1, len(self._tokens(answer))))
        self.calls.append(
            {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "seed": seed,
            }
        )
        return LLMResponse(
            text=answer,
            usage=LLMUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            model_id=self.model_id,
        )
