from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.matched_experiment import MatchedExperimentRunner
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import (
    FunctionalMultiAgentOrganization,
    PaperAgentCommittee,
    SharedKnowledgeOrganization,
)
from csrp_skills.pilot import PilotQuestion
from csrp_skills.pilot_scoring import score_pilot_record
from csrp_skills.providers.openai_responses import create_frozen_means_pilot_adapter
from csrp_skills.registry import SkillRegistry
from csrp_skills.retrieval import FixedEvidenceRetriever
from csrp_skills.runtime import MatchedBudget


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


def blind_id(query_id: str, replicate: int, architecture: str) -> str:
    payload = f"{query_id}|{replicate}|{architecture}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def main() -> None:
    if os.environ.get("CSRP_REAL_LLM_CONFIRM") != "1":
        raise RuntimeError("Set CSRP_REAL_LLM_CONFIRM=1 before making paid external LLM calls.")

    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "benchmark" / "prepilot_v1" / "MINI_PILOT_36CELL_V1.json").read_text(
            encoding="utf-8"
        )
    )
    adapter = create_frozen_means_pilot_adapter()
    registry = build_registry(root)
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    budget = MatchedBudget(
        max_evidence_papers=4,
        max_total_tokens=16000,
        max_output_tokens_per_call=700,
        max_llm_calls=8,
        temperature=0.0,
        seed=None,
    )
    runner = MatchedExperimentRunner(
        retriever=FixedEvidenceRetriever(registry, evidence_budget=4),
        adapter=adapter,
        budget=budget,
        organizations=[
            FunctionalMultiAgentOrganization(registry),
            PaperAgentCommittee(registry),
            SharedKnowledgeOrganization(orchestrator),
        ],
    )
    valid_claim_ids = {
        claim.claim_id for skill in registry.all() for claim in skill.evidence_claims
    }

    out_dir = root / "outputs" / "mini_pilot"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "mini_pilot_raw.json"
    score_path = out_dir / "mini_pilot_automated_scores.json"
    review_path = out_dir / "mini_pilot_blinded_review.csv"
    key_path = out_dir / "mini_pilot_blinding_key.csv"
    progress_path = out_dir / "mini_pilot_progress.json"

    raw = []
    scores = []
    review_rows = []
    key_rows = []

    def checkpoint(status: str, current: dict | None = None) -> None:
        raw_path.write_text(
            json.dumps(
                {
                    "mini_pilot_id": config["mini_pilot_id"],
                    "status": status,
                    "model_id": adapter.model_id,
                    "results": raw,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        score_path.write_text(json.dumps(scores, indent=2), encoding="utf-8")
        progress_path.write_text(
            json.dumps(
                {
                    "status": status,
                    "completed_architecture_cells": len(scores),
                    "expected_cells": config["expected_cells"],
                    "current": current,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    checkpoint("starting")

    for replicate in range(1, config["replicates_per_architecture_query"] + 1):
        for item in config["questions"]:
            question = PilotQuestion.model_validate(item)
            current = {"replicate": replicate, "query_id": question.query_id}
            checkpoint("running", current)
            result = runner.run_query(question.query)
            raw.append(
                {
                    "replicate": replicate,
                    "query_id": question.query_id,
                    **asdict(result),
                }
            )
            for record in result.records:
                score = score_pilot_record(question, record, valid_claim_ids).to_dict()
                score["replicate"] = replicate
                scores.append(score)

                if question.human_review_required:
                    bid = blind_id(question.query_id, replicate, record.architecture)
                    review_rows.append(
                        {
                            "blind_id": bid,
                            "query_id": question.query_id,
                            "replicate": replicate,
                            "query": question.query,
                            "answer": record.answer,
                            "evidence_correctness_1_5": "",
                            "cross_paper_synthesis_1_5": "",
                            "uncertainty_handling_1_5": "",
                            "relation_reasoning_1_5": "",
                            "decision_quality_1_5": "",
                            "unsupported_claim_yes_no": "",
                            "reviewer_notes": "",
                        }
                    )
                    key_rows.append(
                        {
                            "blind_id": bid,
                            "query_id": question.query_id,
                            "replicate": replicate,
                            "architecture": record.architecture,
                        }
                    )
            checkpoint("running", current)

    if len(scores) != config["expected_cells"]:
        checkpoint("failed", {"error": f"expected {config['expected_cells']} cells, got {len(scores)}"})
        raise AssertionError("mini-pilot cell count mismatch")

    with review_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(review_rows[0]) if review_rows else [])
        if review_rows:
            writer.writeheader()
            writer.writerows(review_rows)

    with key_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(key_rows[0]) if key_rows else [])
        if key_rows:
            writer.writeheader()
            writer.writerows(key_rows)

    checkpoint("completed")
    print(raw_path)
    print(score_path)
    print(review_path)
    print(key_path)
    print("model:", adapter.model_id)
    print("architecture-cells:", len(scores))


if __name__ == "__main__":
    main()
