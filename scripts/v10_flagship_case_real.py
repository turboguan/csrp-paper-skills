from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import SharedKnowledgeOrganization
from csrp_skills.providers.openai_responses import create_frozen_means_pilot_adapter
from csrp_skills.registry import SkillRegistry
from csrp_skills.retrieval import FixedEvidenceRetriever
from csrp_skills.runtime import LLMRuntime, MatchedBudget
from csrp_skills.virtual_csrp import VirtualCSRPBlueprint


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
    graph = EvidenceGraph().build_graph(registry.all())
    orchestrator = Orchestrator(registry, graph)
    organization = SharedKnowledgeOrganization(orchestrator)
    retriever = FixedEvidenceRetriever(registry, evidence_budget=4)
    blueprint = VirtualCSRPBlueprint.default()

    query = case["query"]
    packet = retriever.retrieve(query)
    runtime = LLMRuntime(
        adapter,
        MatchedBudget(
            max_evidence_papers=4,
            max_total_tokens=16000,
            max_output_tokens_per_call=1200,
            max_llm_calls=3,
            temperature=0.0,
            seed=None,
        ),
    )
    result = organization.run_matched(packet, runtime)
    plan = {
        "director": blueprint.director,
        "coordinator": blueprint.coordinator,
        "service_channel": case["service_channel"],
        "routed_units": [
            asdict(unit) for unit in blueprint.route_units(query, max_units=4)
        ],
        "governance_roles": list(blueprint.governance_roles),
    }

    out_dir = root / "outputs" / "flagship"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "virtual_csrp_flagship_case_v1.json"
    out.write_text(
        json.dumps(
            {
                "case_id": case["case_id"],
                "status": "completed_live_llm_flagship_case",
                "model_id": adapter.model_id,
                "institutional_plan": plan,
                "retrieved_papers": packet.paper_ids,
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
    print("retrieved papers:", packet.paper_ids)


if __name__ == "__main__":
    main()
