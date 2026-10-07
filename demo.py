from __future__ import annotations

import json
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parent


def build_system() -> Orchestrator:
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    for path in sorted((ROOT / "sample_skills").glob("*.json")):
        registry.register(factory.from_json(path))
    graph = EvidenceGraph().build_graph(registry.all())
    return Orchestrator(registry, graph)


def main():
    system = build_system()
    queries = [
        "What population was studied in SYN-001?",
        "What does the synthetic evidence say about school-based psychoeducation and suicidal ideation in adolescents?",
        "Are the media reporting guideline findings consistent across the synthetic studies?",
        "Can adolescent school-based evidence be generalized to older adults?",
        "What is my suicide risk percentage based on these studies?",
    ]
    outputs = []
    for query in queries:
        result = system.run(query)
        outputs.append(result.to_dict())
        print("=" * 88)
        print(query)
        print(result.answer)
        print("Selected:", result.selected_paper_ids)
        print("Judge:", result.judge.label.value)
        print("Safety:", result.safety.action.value)
        print("Metrics:", result.metrics.to_dict())

    out = ROOT / "outputs" / "demo_output.json"
    out.write_text(json.dumps(outputs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
