from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.llm import DeterministicTestLLMAdapter
from csrp_skills.matched_experiment import MatchedExperimentRunner
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import (
    FunctionalMultiAgentOrganization,
    PaperAgentCommittee,
    SharedKnowledgeOrganization,
)
from csrp_skills.pilot import PilotQuestion
from csrp_skills.pilot_scoring import score_pilot_record
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


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "benchmark" / "prepilot_v1" / "MINI_PILOT_36CELL_V1.json").read_text(
            encoding="utf-8"
        )
    )
    registry = build_registry(root)
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    adapter = DeterministicTestLLMAdapter()
    budget = MatchedBudget(
        max_evidence_papers=4,
        max_total_tokens=16000,
        max_output_tokens_per_call=700,
        max_llm_calls=8,
        temperature=0.0,
        seed=42,
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
    records = []
    scores = []
    for replicate in range(1, config["replicates_per_architecture_query"] + 1):
        for item in config["questions"]:
            question = PilotQuestion.model_validate(item)
            result = runner.run_query(question.query)
            records.append(
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

    expected = config["expected_cells"]
    if len(scores) != expected:
        raise AssertionError(f"expected {expected} architecture cells, got {len(scores)}")

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v10_36cell_mini_pilot_dry_run.json"
    out.write_text(
        json.dumps(
            {
                "status": "deterministic_pipeline_check_not_scientific_result",
                "mini_pilot_id": config["mini_pilot_id"],
                "cells": len(scores),
                "records": records,
                "scores": scores,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(out)
    print("questions:", len(config["questions"]))
    print("replicates:", config["replicates_per_architecture_query"])
    print("architecture-cells:", len(scores))
    print("NOTE: deterministic adapter only; not a scientific result.")


if __name__ == "__main__":
    main()
