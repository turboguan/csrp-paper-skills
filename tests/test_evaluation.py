from pathlib import Path

from csrp_skills.baselines import MonolithicAgentRunner, OnePaperOneAgentRunner, PaperAsSkillRunner, RAGOnlyRunner
from csrp_skills.evaluation import load_queries, run_query_suite
from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parents[1]


def _means_system():
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    paths = [
        ROOT / "real_skills" / "CSRP-REAL-004.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]
    for path in paths:
        registry.register(factory.from_json(path))
    return Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))


def test_means_query_set_loads():
    queries = load_queries(ROOT / "benchmark" / "v0.3" / "means_restriction_queries.json")
    assert len(queries) == 5
    assert any(q.task_type == "contradiction_vs_qualification" for q in queries)


def test_dry_run_marks_unimplemented_baselines_not_ready():
    queries = load_queries(ROOT / "benchmark" / "v0.3" / "means_restriction_queries.json")[:1]
    records = run_query_suite(
        queries,
        [RAGOnlyRunner(), MonolithicAgentRunner(), OnePaperOneAgentRunner(), PaperAsSkillRunner(_means_system())],
    )
    status = {r.architecture: r.status for r in records}
    assert status["rag_only"] == "not_ready"
    assert status["monolithic_agent"] == "not_ready"
    assert status["one_paper_one_agent"] == "not_ready"
    assert status["paper_as_skill"] == "completed"
