from __future__ import annotations

import json
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.llm import DeterministicTestLLMAdapter
from csrp_skills.minimal_virtual_csrp import MinimalVirtualCSRPLLMOrganization
from csrp_skills.orchestrator import Orchestrator
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
    root = Path(__file__).resolve().parents[1]
    case = json.loads(
        (root / "benchmark" / "prepilot_v1" / "FLAGSHIP_CASE_V1.json").read_text(
            encoding="utf-8"
        )
    )

    registry = build_registry(root)
    EvidenceGraph().build_graph(registry.all())  # validates graph construction
    retriever = FixedEvidenceRetriever(registry, evidence_budget=4)
    packet = retriever.retrieve(case["query"])

    org = MinimalVirtualCSRPLLMOrganization()
    runtime = LLMRuntime(
        DeterministicTestLLMAdapter(),
        MatchedBudget(
            max_evidence_papers=4,
            max_total_tokens=16000,
            max_output_tokens_per_call=1200,
            max_llm_calls=4,
            temperature=0.0,
            seed=42,
        ),
    )
    result = org.run_matched(packet, runtime, output_mode="policy")

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v11_minimal_virtual_csrp_dry_run.json"
    out.write_text(
        json.dumps(
            {
                "status": "deterministic_pipeline_check_not_scientific_result",
                "architecture": result.architecture,
                "query": result.query,
                "selected_paper_ids": result.selected_paper_ids,
                "answer": result.answer,
                "provenance": result.provenance,
                "metrics": result.metrics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(out)
    print("architecture:", result.architecture)
    print("persistent agents:", result.metrics["persistent_agents"])
    print("active agents:", result.metrics["active_agents"])
    print("llm calls:", result.metrics["llm_calls"])
    print("NOTE: deterministic adapter only; not a scientific result.")


if __name__ == "__main__":
    main()
