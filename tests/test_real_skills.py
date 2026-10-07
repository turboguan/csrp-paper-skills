from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parents[1]


def build_real_system():
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    for path in sorted((ROOT / "real_skills").glob("*.json")):
        registry.register(factory.from_json(path))
    graph = EvidenceGraph().build_graph(registry.all())
    return Orchestrator(registry, graph)


def test_real_skill_records_validate_and_have_provenance():
    factory = PaperToSkillFactory()
    paths = sorted((ROOT / "real_skills").glob("*.json"))
    assert len(paths) == 5
    for path in paths:
        skill = factory.from_json(path)
        assert skill.metadata["record_status"] == "real_publication"
        assert skill.metadata["human_validation_status"] == "model_curated_not_expert_validated"
        assert all(claim.provenance for claim in skill.evidence_claims)


def test_real_exact_id_retrieval():
    system = build_real_system()
    result = system.run("What did CSRP-REAL-004 report about charcoal-burning suicide rates?")
    assert result.selected_paper_ids == ["CSRP-REAL-004"]
    assert any(cid.startswith("CSRP-REAL-004-") for cid in result.provenance)


def test_real_spatial_query_does_not_trigger_individual_route():
    system = build_real_system()
    result = system.run(
        "How can spatial suicide-cluster evidence inform community prevention without being used for individual risk prediction?"
    )
    assert result.route.agent == "Universal"
    assert result.selected_paper_ids == ["CSRP-REAL-002"]


def test_real_safety_preflight_blocks_individual_risk_scoring_before_retrieval():
    system = build_real_system()
    result = system.run("Based on these CSRP studies, what is my suicide risk percentage?")
    assert result.safety.action.value == "escalate"
    assert result.selected_paper_ids == []
    assert result.metrics.evidence_count == 0


def test_graph_has_curated_related_paper_edge():
    system = build_real_system()
    edge_data = system.graph.g.get_edge_data("paper:CSRP-REAL-002", "paper:CSRP-REAL-004")
    assert edge_data is not None
    assert any(d.get("relation") == "RELATED_TO" for d in edge_data.values())
