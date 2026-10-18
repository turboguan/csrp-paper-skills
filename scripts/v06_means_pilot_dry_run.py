from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.llm import DeterministicTestLLMAdapter
from csrp_skills.matched_experiment import MatchedExperimentRunner
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import FunctionalMultiAgentOrganization, PaperAgentCommittee, SharedKnowledgeOrganization
from csrp_skills.pilot import load_means_pilot
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
    suite = load_means_pilot(root / "benchmark" / "v0.6" / "means_pilot_questions_v1.json")
    registry = build_registry(root)
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    budget = MatchedBudget(
        max_evidence_papers=4,
        max_total_tokens=16000,
        max_output_tokens_per_call=700,
        max_llm_calls=8,
        temperature=0.0,
        seed=42,
    )
    adapter = DeterministicTestLLMAdapter()
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

    valid_claim_ids = {claim.claim_id for skill in registry.all() for claim in skill.evidence_claims}
    raw_results = []
    scores = []
    by_query = {q.query_id: q for q in suite.questions}

    for question in suite.questions:
        result = runner.run_query(question.query)
        raw_results.append(asdict(result))
        for record in result.records:
            scores.append(score_pilot_record(question, record, valid_claim_ids).to_dict())

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "pilot_id": suite.pilot_id,
        "status": "deterministic_pipeline_dry_run_not_scientific_result",
        "adapter": adapter.model_id,
        "question_count": len(suite.questions),
        "architecture_count": 3,
        "results": raw_results,
        "automated_scores": scores,
    }
    out = out_dir / "v06_means_pilot_dry_run.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(out)
    print("questions:", len(suite.questions))
    print("architecture-cells:", len(scores))
    print("NOTE: deterministic test adapter only; not a real LLM performance result.")


if __name__ == "__main__":
    main()
