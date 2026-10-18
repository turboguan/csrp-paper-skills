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
    retriever = FixedEvidenceRetriever(registry, evidence_budget=budget.max_evidence_papers)
    runner = MatchedExperimentRunner(
        retriever=retriever,
        adapter=adapter,
        budget=budget,
        organizations=[
            FunctionalMultiAgentOrganization(registry),
            PaperAgentCommittee(registry),
            SharedKnowledgeOrganization(orchestrator),
        ],
    )

    queries = [
        "What evidence supports or limits the effectiveness of restricting retail access to barbecue charcoal as a population suicide-prevention strategy?",
        "Compare the 2015 short-term and 2021 long-term New Taipei charcoal-restriction findings.",
        "Do the charcoal-restriction studies show that the intervention improves depression symptoms?",
    ]
    results = [runner.run_query(query) for query in queries]

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v05_matched_llm_dry_run.json"
    out.write_text(json.dumps([asdict(result) for result in results], indent=2), encoding="utf-8")
    print(out)
    print("model:", adapter.model_id)
    print("queries:", len(results))
    print("architectures:", len(runner.organizations))
    print("NOTE: deterministic test adapter only; this is not an LLM performance benchmark.")


if __name__ == "__main__":
    main()
