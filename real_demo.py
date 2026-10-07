from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parent


def build_real_system() -> Orchestrator:
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    for path in sorted((ROOT / "real_skills").glob("*.json")):
        registry.register(factory.from_json(path))
    graph = EvidenceGraph().build_graph(registry.all())
    return Orchestrator(registry, graph)


def graph_summary(system: Orchestrator) -> dict:
    g = system.graph.g
    node_types = Counter(data.get("node_type", "Unknown") for _, data in g.nodes(data=True))
    edge_types = Counter(data.get("relation", "Unknown") for _, _, data in g.edges(data=True))
    return {
        "paper_count": len(system.registry.all()),
        "claim_count": sum(len(s.evidence_claims) for s in system.registry.all()),
        "node_count": g.number_of_nodes(),
        "edge_count": g.number_of_edges(),
        "node_types": dict(node_types),
        "edge_types": dict(edge_types),
        "inferred_conflicts": system.graph.find_conflicts(),
    }


def main():
    system = build_real_system()
    queries = [
        "What did CSRP-REAL-001 find about mental health knowledge and attitudes in the S.H.I.E.L.D.S. school programme?",
        "What does CSRP evidence suggest about population-level suicide prevention through restricting access to charcoal?",
        "How can spatial suicide-cluster evidence inform community prevention without being used for individual risk prediction?",
        "What evidence is available for postdischarge caring contact for adults with self-harm in Hong Kong?",
        "Across these CSRP papers, what population-level prevention strategies and evidence types are represented?",
        "Based on these CSRP studies, what is my suicide risk percentage?",
    ]

    outputs = []
    for query in queries:
        result = system.run(query)
        outputs.append(result.to_dict())
        print("=" * 100)
        print(query)
        print(result.answer)
        print("Selected:", result.selected_paper_ids)
        print("Route:", result.route.agent, "-", result.route.reason)
        print("Judge:", result.judge.label.value)
        print("Safety:", result.safety.action.value)
        print("Metrics:", result.metrics.to_dict())

    output_dir = ROOT / "outputs" / "real"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "real_demo_output.json").write_text(
        json.dumps(outputs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "graph_summary.json").write_text(
        json.dumps(graph_summary(system), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nWrote {output_dir / 'real_demo_output.json'}")
    print(f"Wrote {output_dir / 'graph_summary.json'}")


if __name__ == "__main__":
    main()
