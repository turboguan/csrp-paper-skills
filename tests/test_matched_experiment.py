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

ROOT = Path(__file__).resolve().parents[1]


def _runner(evidence_budget=4):
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    for path in [
        ROOT / "real_skills" / "CSRP-REAL-004.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]:
        registry.register(factory.from_json(path))
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    budget = MatchedBudget(
        max_evidence_papers=evidence_budget,
        max_total_tokens=16000,
        max_output_tokens_per_call=700,
        max_llm_calls=8,
        temperature=0.0,
        seed=42,
    )
    adapter = DeterministicTestLLMAdapter()
    return MatchedExperimentRunner(
        retriever=FixedEvidenceRetriever(registry, evidence_budget=evidence_budget),
        adapter=adapter,
        budget=budget,
        organizations=[
            FunctionalMultiAgentOrganization(registry),
            PaperAgentCommittee(registry),
            SharedKnowledgeOrganization(orchestrator),
        ],
    )


def test_all_architectures_receive_identical_evidence_packet_and_model():
    runner = _runner()
    result = runner.run_query(
        "What evidence supports or limits the effectiveness of restricting retail access to barbecue charcoal?"
    )
    expected = result.evidence_packet["paper_ids"]
    assert expected
    assert all(record.selected_paper_ids == expected for record in result.records)
    assert {record.metrics["model_id"] for record in result.records} == {runner.adapter.model_id}
    assert {record.metrics["retriever_id"] for record in result.records} == {result.evidence_packet["retriever_id"]}


def test_same_evidence_and_total_token_budget_is_enforced():
    runner = _runner(evidence_budget=3)
    result = runner.run_query(
        "Compare the 2015 short-term and 2021 long-term New Taipei charcoal-restriction findings."
    )
    assert len(result.evidence_packet["paper_ids"]) <= 3
    for record in result.records:
        assert record.metrics["evidence_budget"] == 3
        assert record.metrics["budget"]["max_total_tokens"] == 16000
        assert record.metrics["total_tokens"] <= 16000
        assert record.metrics["budget"]["max_output_tokens_per_call"] == 700
        assert record.metrics["budget"]["temperature"] == 0.0
        assert record.metrics["budget"]["seed"] == 42


def test_coordination_call_counts_are_measured_not_forced_equal():
    runner = _runner(evidence_budget=4)
    result = runner.run_query(
        "What evidence supports or limits the effectiveness of restricting retail access to barbecue charcoal?"
    )
    by_arch = {record.architecture: record for record in result.records}
    assert by_arch["functional_multi_agent"].metrics["llm_calls"] == 5
    committee = by_arch["paper_agent_committee"]
    assert committee.metrics["llm_calls"] == len(committee.selected_paper_ids) + 1
    assert by_arch["shared_knowledge_umbrella"].metrics["llm_calls"] == 1


def test_hard_negative_uses_same_retriever_and_calls_no_llm():
    runner = _runner()
    result = runner.run_query(
        "Do the charcoal-restriction studies show that the intervention improves depression symptoms?"
    )
    assert result.evidence_packet["paper_ids"] == []
    for record in result.records:
        assert record.selected_paper_ids == []
        assert record.provenance == {}
        assert record.metrics.get("llm_calls", 0) == 0
        assert "No relevant validated claims were retrieved." in record.answer
