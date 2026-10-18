from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.organizations import (
    FunctionalMultiAgentOrganization,
    PaperAgentCommittee,
    SharedKnowledgeOrganization,
)
from csrp_skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parents[1]


def _registry():
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    for path in [
        ROOT / "real_skills" / "CSRP-REAL-004.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]:
        registry.register(factory.from_json(path))
    return registry


def _organizations():
    registry = _registry()
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    return [
        FunctionalMultiAgentOrganization(registry),
        PaperAgentCommittee(registry),
        SharedKnowledgeOrganization(orchestrator),
    ]


def test_three_organizational_architectures_are_runnable():
    query = "Compare the 2015 short-term and 2021 long-term New Taipei charcoal-restriction findings."
    results = [org.run(query) for org in _organizations()]
    assert {r.architecture for r in results} == {
        "functional_multi_agent",
        "paper_agent_committee",
        "shared_knowledge_umbrella",
    }
    assert all(r.selected_paper_ids for r in results)
    assert all(r.provenance for r in results)


def test_functional_architecture_exposes_expected_roles():
    registry = _registry()
    result = FunctionalMultiAgentOrganization(registry).run(
        "What evidence supports or limits the effectiveness of restricting retail access to barbecue charcoal?"
    )
    actors = {message.actor for message in result.transcript}
    assert {
        "FacilitatorAgent",
        "PerspectiveAgent",
        "PredictAgent",
        "StrategyAgent",
        "ExternalAgent",
        "DecisionAgent",
    }.issubset(actors)
    assert result.metrics["shared_evidence_context"] is True
    assert result.metrics["paper_agents"] == 0


def test_committee_creates_one_paper_agent_per_retrieved_paper():
    registry = _registry()
    result = PaperAgentCommittee(registry).run(
        "What evidence supports or limits the effectiveness of restricting retail access to barbecue charcoal?"
    )
    paper_agents = [m for m in result.transcript if m.role == "paper_expert"]
    assert len(paper_agents) == len(result.selected_paper_ids)
    assert result.metrics["paper_agents"] == len(result.selected_paper_ids)
    assert result.metrics["shared_evidence_context"] is False


def test_shared_knowledge_uses_no_persistent_paper_agents():
    registry = _registry()
    orchestrator = Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))
    result = SharedKnowledgeOrganization(orchestrator).run(
        "Compare the 2015 short-term and 2021 long-term New Taipei charcoal-restriction findings."
    )
    assert result.metrics["paper_agents"] == 0
    assert result.metrics["shared_evidence_context"] is True
    assert {m.actor for m in result.transcript} == {
        "InstitutionalOrchestrator",
        "EvidenceJudge",
        "SafetySupervisor",
    }


def test_all_architectures_fail_closed_on_wrong_outcome_hard_negative():
    query = "Do the charcoal-restriction studies show that the intervention improves depression symptoms?"
    for organization in _organizations():
        result = organization.run(query)
        assert result.selected_paper_ids == []
        assert result.provenance == {}
        assert "No relevant validated claims were retrieved." in result.answer
