from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.llm import DeterministicTestLLMAdapter
from csrp_skills.minimal_virtual_csrp import MinimalVirtualCSRPLLMOrganization
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import FunctionalMultiAgentOrganization, SharedKnowledgeOrganization
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


def blind_id(flagship_id: str, architecture: str) -> str:
    return hashlib.sha256(f"{flagship_id}|{architecture}".encode("utf-8")).hexdigest()[:12]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "benchmark" / "v1.3" / "FLAGSHIP_THREE_ARCHITECTURE_V1.json").read_text(
            encoding="utf-8"
        )
    )

    registry = build_registry(root)
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    retriever = FixedEvidenceRetriever(registry, evidence_budget=4)
    packet = retriever.retrieve(config["query"])

    adapter = DeterministicTestLLMAdapter()
    budget = MatchedBudget(
        max_evidence_papers=4,
        max_total_tokens=16000,
        max_output_tokens_per_call=1200,
        max_llm_calls=8,
        temperature=0.0,
        seed=42,
    )

    organizations = [
        FunctionalMultiAgentOrganization(registry),
        MinimalVirtualCSRPLLMOrganization(),
        SharedKnowledgeOrganization(orchestrator),
    ]

    records = []
    review_rows = []
    key_rows = []

    for organization in organizations:
        runtime = LLMRuntime(adapter, budget)
        if organization.architecture_name == "minimal_virtual_csrp":
            result = organization.run_matched(packet, runtime, output_mode="policy")
        else:
            result = organization.run_matched(packet, runtime)

        if result.selected_paper_ids != packet.paper_ids:
            raise AssertionError(
                f"{result.architecture} changed the matched EvidencePacket"
            )
        if result.metrics.get("total_tokens", 0) > budget.max_total_tokens:
            raise AssertionError(
                f"{result.architecture} exceeded the total token ceiling"
            )

        records.append(
            {
                "architecture": result.architecture,
                "answer": result.answer,
                "selected_paper_ids": result.selected_paper_ids,
                "provenance": result.provenance,
                "transcript": [asdict(message) for message in result.transcript],
                "metrics": result.metrics,
            }
        )

        bid = blind_id(config["flagship_id"], result.architecture)
        review_rows.append(
            {
                "blind_id": bid,
                "query": config["query"],
                "answer": result.answer,
                "evidence_correctness_1_5": "",
                "cross_paper_synthesis_1_5": "",
                "uncertainty_handling_1_5": "",
                "policy_usefulness_1_5": "",
                "provenance_quality_1_5": "",
                "unsupported_claim_yes_no": "",
                "reviewer_notes": "",
            }
        )
        key_rows.append(
            {
                "blind_id": bid,
                "architecture": result.architecture,
            }
        )

    observed = [record["architecture"] for record in records]
    if observed != config["architectures"]:
        raise AssertionError(
            f"architecture order mismatch: observed={observed}, expected={config['architectures']}"
        )

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = out_dir / "v13_flagship_three_architectures_dry_run.json"
    raw.write_text(
        json.dumps(
            {
                "status": "deterministic_pipeline_check_not_scientific_result",
                "flagship_id": config["flagship_id"],
                "evidence_packet": {
                    "retriever_id": packet.retriever_id,
                    "evidence_budget": packet.evidence_budget,
                    "paper_ids": packet.paper_ids,
                },
                "records": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    review = out_dir / "v13_flagship_blinded_review.csv"
    with review.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(review_rows[0]))
        writer.writeheader()
        writer.writerows(review_rows)

    key = out_dir / "v13_flagship_blinding_key.csv"
    with key.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)

    print(raw)
    print("evidence packet:", packet.paper_ids)
    for record in records:
        print(
            record["architecture"],
            "llm_calls=", record["metrics"].get("llm_calls"),
            "tokens=", record["metrics"].get("total_tokens"),
            "coordination_messages=", record["metrics"].get("coordination_messages"),
        )
    print("NOTE: deterministic adapter only; not a scientific result.")


if __name__ == "__main__":
    main()
