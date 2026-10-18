from __future__ import annotations

import csv
import importlib
import json
import os
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.llm import LLMAdapter
from csrp_skills.matched_experiment import MatchedExperimentRunner
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import FunctionalMultiAgentOrganization, PaperAgentCommittee, SharedKnowledgeOrganization
from csrp_skills.pilot import load_means_pilot
from csrp_skills.pilot_scoring import score_pilot_record
from csrp_skills.registry import SkillRegistry
from csrp_skills.retrieval import FixedEvidenceRetriever
from csrp_skills.runtime import MatchedBudget


def load_adapter() -> LLMAdapter:
    target = os.environ.get("CSRP_ADAPTER_FACTORY", "")
    if not target or ":" not in target:
        raise RuntimeError(
            "Set CSRP_ADAPTER_FACTORY='package.module:function'. The function must return one fixed LLMAdapter instance."
        )
    module_name, function_name = target.split(":", 1)
    factory = getattr(importlib.import_module(module_name), function_name)
    adapter = factory()
    if not isinstance(adapter, LLMAdapter):
        raise TypeError("adapter factory must return an LLMAdapter")
    return adapter


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
        raise RuntimeError("Set CSRP_REAL_LLM_CONFIRM=1 to acknowledge this will make paid external LLM calls.")

    root = Path(__file__).resolve().parents[1]
    suite = load_means_pilot(root / "benchmark" / "v0.6" / "means_pilot_questions_v1.json")
    config = json.loads((root / "benchmark" / "v0.5" / "matched_experiment_config.json").read_text(encoding="utf-8"))
    adapter = load_adapter()
    frozen_model = config["model_id"]
    if frozen_model == "SET_ONE_FIXED_MODEL_ID_BEFORE_EXPERIMENT":
        raise RuntimeError("Freeze benchmark/v0.5/matched_experiment_config.json:model_id before a real pilot run.")
    if adapter.model_id != frozen_model:
        raise RuntimeError(f"Adapter model_id {adapter.model_id!r} does not match frozen model_id {frozen_model!r}.")

    registry = build_registry(root)
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    token_cfg = config["token_budget"]
    budget = MatchedBudget(
        max_evidence_papers=config["evidence_budget_papers"],
        max_total_tokens=token_cfg["max_total_tokens"],
        max_output_tokens_per_call=token_cfg["max_output_tokens_per_call"],
        max_llm_calls=token_cfg["max_llm_calls"],
        temperature=token_cfg["temperature"],
        seed=token_cfg.get("seed"),
    )
    runner = MatchedExperimentRunner(
        retriever=FixedEvidenceRetriever(registry, evidence_budget=budget.max_evidence_papers),
        adapter=adapter,
        budget=budget,
        organizations=[
            FunctionalMultiAgentOrganization(registry),
            PaperAgentCommittee(registry),
            SharedKnowledgeOrganization(orchestrator),
        ],
    )

    valid_claim_ids = {claim.claim_id for skill in registry.all() for claim in skill.evidence_claims}
    raw = []
    scores = []
    review_rows = []

    for replicate in range(1, suite.replicates_per_architecture_query + 1):
        for question in suite.questions:
            result = runner.run_query(question.query)
            raw.append({"replicate": replicate, **asdict(result)})
            for record in result.records:
                score = score_pilot_record(question, record, valid_claim_ids).to_dict()
                score["replicate"] = replicate
                scores.append(score)
                if question.human_review_required:
                    review_rows.append({
                        "query_id": question.query_id,
                        "replicate": replicate,
                        "architecture": record.architecture,
                        "complexity": question.complexity,
                        "task_interdependence": question.task_interdependence,
                        "task_uncertainty": question.task_uncertainty,
                        "evidence_correctness_1_5": "",
                        "cross_paper_synthesis_1_5": "",
                        "uncertainty_handling_1_5": "",
                        "relation_reasoning_1_5": "",
                        "decision_quality_1_5": "",
                        "unsupported_claim_present_yes_no": "",
                        "reviewer_notes": "",
                    })

    out_dir = root / "outputs" / "pilot"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "means_pilot_v1_raw.json"
    score_path = out_dir / "means_pilot_v1_automated_scores.json"
    review_path = out_dir / "means_pilot_v1_human_review.csv"
    raw_path.write_text(json.dumps({
        "pilot_id": suite.pilot_id,
        "model_id": adapter.model_id,
        "replicates": suite.replicates_per_architecture_query,
        "results": raw,
    }, indent=2), encoding="utf-8")
    score_path.write_text(json.dumps(scores, indent=2), encoding="utf-8")

    fieldnames = list(review_rows[0]) if review_rows else []
    with review_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            writer.writerows(review_rows)

    print(raw_path)
    print(score_path)
    print(review_path)
    print("model:", adapter.model_id)
    print("architecture-query-replicate cells:", len(scores))


if __name__ == "__main__":
    main()
