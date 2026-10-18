import json
from pathlib import Path

from csrp_skills.llm import LLMAdapter, LLMMessage, LLMResponse, LLMUsage
from csrp_skills.runtime import LLMRuntime, MatchedBudget

ROOT = Path(__file__).resolve().parents[1]


class ApproximateCountAdapter(LLMAdapter):
    model_id = "fake-provider-model"
    token_count_is_exact = False

    def count_tokens(self, messages):
        return 10

    def generate(self, messages, *, max_output_tokens, temperature, seed):
        # Simulate provider-reported protocol overhead exceeding local estimate.
        return LLMResponse(
            text="ok",
            usage=LLMUsage(input_tokens=18, output_tokens=1),
            model_id=self.model_id,
        )


def test_openai_model_is_frozen_for_means_pilot():
    config = json.loads(
        (ROOT / "benchmark" / "v0.5" / "matched_experiment_config.json").read_text(
            encoding="utf-8"
        )
    )
    assert config["status"] == "frozen_for_means_pilot_v1"
    assert config["provider"] == "openai"
    assert config["api"] == "responses"
    assert config["model_id"] == "gpt-6.1-sol"
    assert config["service_tier"] == "default"
    assert config["token_budget"]["seed"] is None


def test_provider_reported_usage_is_authoritative_for_inexact_adapter():
    runtime = LLMRuntime(
        ApproximateCountAdapter(),
        MatchedBudget(
            max_total_tokens=1000,
            max_output_tokens_per_call=100,
            max_llm_calls=2,
            temperature=0.0,
            seed=None,
        ),
    )
    response = runtime.generate([LLMMessage(role="user", content="test")])
    assert response.usage.input_tokens == 18
    assert runtime.metrics()["input_tokens"] == 18
    assert runtime.metrics()["total_tokens"] == 19
