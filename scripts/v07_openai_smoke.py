from __future__ import annotations

import os

from csrp_skills.llm import LLMMessage
from csrp_skills.providers.openai_responses import create_frozen_means_pilot_adapter


def main() -> None:
    if os.environ.get("CSRP_REAL_LLM_CONFIRM") != "1":
        raise RuntimeError("Set CSRP_REAL_LLM_CONFIRM=1 before making a paid API call.")

    adapter = create_frozen_means_pilot_adapter()
    response = adapter.generate(
        [
            LLMMessage(
                role="user",
                content="Credential and model-access smoke test. Reply with exactly: OK",
            )
        ],
        max_output_tokens=32,
        temperature=0.0,
        seed=None,
    )
    print("model:", response.model_id)
    print("input_tokens:", response.usage.input_tokens)
    print("output_tokens:", response.usage.output_tokens)
    print("response:", response.text.strip())


if __name__ == "__main__":
    main()
