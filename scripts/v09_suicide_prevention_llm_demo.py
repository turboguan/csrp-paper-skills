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
    for paper_id in [
        "CSRP-REAL-001",
        "CSRP-REAL-002",
        "CSRP-REAL-003",
        "CSRP-REAL-004",
        "CSRP-REAL-005",
    ]:
        registry.register(factory.from_json(root / "real_skills" / f"{paper_id}.json"))
    return registry


def main() -> None:
    if os.environ.get("CSRP_REAL_LLM_CONFIRM") != "1":
        raise RuntimeError(
            "Set CSRP_REAL_LLM_CONFIRM=1 to acknowledge that this demo makes paid external LLM calls."
        )

    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "benchmark" / "v0.9" / "suicide_prevention_llm_demo_v1.json").read_text(
            encoding="utf-8"
        )
    )

    adapter = create_frozen_means_pilot_adapter()
    if adapter.model_id != config["model_id"]:
        raise RuntimeError(
            f"Adapter model {adapter.model_id!r} does not match demo model {config['model_id']!r}."
        )

    registry = build_registry(root)
    graph = EvidenceGraph().build_graph(registry.all())
    orchestrator = Orchestrator(registry, graph)
    organization = SharedKnowledgeOrganization(orchestrator)
    retriever = FixedEvidenceRetriever(registry, evidence_budget=5)
    blueprint = VirtualCSRPBlueprint.default()

    out_dir = root / "outputs" / "virtual_csrp"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "suicide_prevention_llm_demo_v1.json"

    records = []
    for item in config["questions"]:
        query = item["query"]
        packet = retriever.retrieve(query)
        runtime = LLMRuntime(
            adapter,
            MatchedBudget(
                max_evidence_papers=5,
                max_total_tokens=12000,
                max_output_tokens_per_call=900,
                max_llm_calls=2,
                temperature=0.0,
                seed=None,
            ),
        )
        plan = {
            "director": blueprint.director,
            "coordinator": blueprint.coordinator,
            "routed_units": [
                asdict(unit) for unit in blueprint.route_units(query, max_units=3)
            ],
            "governance_roles": list(blueprint.governance_roles),
        }
        result = organization.run_matched(packet, runtime)
        records.append(
            {
                "query_id": item["query_id"],
                "theme": item["theme"],
                "query": query,
                "institutional_plan": plan,
                "expected_papers": item["expected_papers"],
                "retrieved_papers": packet.paper_ids,
                "answer": result.answer,
                "provenance": result.provenance,
                "transcript": [asdict(message) for message in result.transcript],
                "metrics": result.metrics,
            }
        )
        output_path.write_text(
            json.dumps(
                {
                    "demo_id": config["demo_id"],
                    "status": "running",
                    "model_id": adapter.model_id,
                    "records": records,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    output_path.write_text(
        json.dumps(
            {
                "demo_id": config["demo_id"],
                "status": "completed",
                "model_id": adapter.model_id,
                "records": records,
                "interpretation_boundary": config["interpretation_boundary"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(output_path)
    print("model:", adapter.model_id)
    print("questions:", len(records))
    print("NOTE: live LLM smoke demo only; not a benchmark result.")


if __name__ == "__main__":
    main()
