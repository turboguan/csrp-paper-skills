from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.minimal_virtual_csrp import MinimalVirtualCSRPLLMOrganization
from csrp_skills.providers.openai_responses import create_frozen_means_pilot_adapter
from csrp_skills.registry import SkillRegistry
from csrp_skills.retrieval import FixedEvidenceRetriever
from csrp_skills.runtime import LLMRuntime, MatchedBudget


def build_registry(root: Path) -> SkillRegistry:
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    for path in [
        root / "real_skills" / "CSRP-REAL-004.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]:
        registry.register(factory.from_json(path))
    return registry


def main() -> None:
    if os.environ.get("CSRP_REAL_LLM_CONFIRM") != "1":
        raise RuntimeError("Set CSRP_REAL_LLM_CONFIRM=1 before making paid external LLM calls.")

    root = Path(__file__).resolve().parents[1]
    case = json.loads(
        (root / "benchmark" / "prepilot_v1" / "FLAGSHIP_CASE_V1.json").read_text(
            encoding="utf-8"
        )
    )
    adapter = create_frozen_means_pilot_adapter()
    registry = build_registry(root)
    packet = FixedEvidenceRetriever(registry, evidence_budget=4).retrieve(case["query"])

    org = MinimalVirtualCSRPLLMOrganization()
    runtime = LLMRuntime(
        adapter,
        MatchedBudget(
            max_evidence_papers=4,
            max_total_tokens=16000,
            max_output_tokens_per_call=1200,
            max_llm_calls=4,
            temperature=0.0,
            seed=None,
        ),
    )
    result = org.run_matched(packet, runtime, output_mode="policy")

    out_dir = root / "outputs" / "flagship"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v11_minimal_virtual_csrp_flagship.json"
    out.write_text(
        json.dumps(
            {
                "status": "completed_live_llm_flagship_case",
                "model_id": adapter.model_id,
                "architecture": result.architecture,
                "query": result.query,
                "selected_paper_ids": result.selected_paper_ids,
                "answer": result.answer,
                "provenance": result.provenance,
                "transcript": [asdict(message) for message in result.transcript],
                "metrics": result.metrics,
                "boundary": case["boundary"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(out)
    print("model:", adapter.model_id)
    print("active agents:", result.metrics["active_agents"])
    print("llm calls:", result.metrics["llm_calls"])


if __name__ == "__main__":
    main()
