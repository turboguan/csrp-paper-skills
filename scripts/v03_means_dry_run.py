from __future__ import annotations

import json
from pathlib import Path

from csrp_skills.baselines import (
    MonolithicAgentRunner,
    OnePaperOneAgentRunner,
    PaperAsSkillRunner,
    RAGOnlyRunner,
)
from csrp_skills.evaluation import load_queries, run_query_suite
from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry


def build_means_system(root: Path) -> Orchestrator:
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    paths = [
        root / "real_skills" / "CSRP-REAL-004.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]
    for path in paths:
        registry.register(factory.from_json(path))
    graph = EvidenceGraph().build_graph(registry.all())
    return Orchestrator(registry, graph)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    queries = load_queries(root / "benchmark" / "v0.3" / "means_restriction_queries.json")
    system = build_means_system(root)
    runners = [
        RAGOnlyRunner(),
        MonolithicAgentRunner(),
        OnePaperOneAgentRunner(),
        PaperAsSkillRunner(system),
    ]
    records = run_query_suite(queries, runners)
    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v03_means_dry_run.json"
    out.write_text(json.dumps([r.model_dump() for r in records], indent=2), encoding="utf-8")
    print(out)
    print("completed:", sum(r.status == "completed" for r in records))
    print("not_ready:", sum(r.status == "not_ready" for r in records))
    print("NOTE: this is a harness dry-run, not a four-system benchmark result.")


if __name__ == "__main__":
    main()
