from __future__ import annotations

import json
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
    graph = EvidenceGraph().build_graph(registry.all())
    orchestrator = Orchestrator(registry, graph)

    organizations = [
        FunctionalMultiAgentOrganization(registry),
        PaperAgentCommittee(registry),
        SharedKnowledgeOrganization(orchestrator),
    ]

    queries = [
        "What evidence supports or limits the effectiveness of restricting retail access to barbecue charcoal as a population suicide-prevention strategy?",
        "Compare the 2015 short-term and 2021 long-term New Taipei charcoal-restriction findings.",
        "Do the charcoal-restriction studies show that the intervention improves depression symptoms?",
    ]

    records = []
    for query in queries:
        for organization in organizations:
            records.append(organization.run(query).to_dict())

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v04_organizational_designs_dry_run.json"
    out.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(out)
    print(f"architectures: {len(organizations)}")
    print(f"queries: {len(queries)}")
    print("NOTE: deterministic architecture scaffold only; not an LLM benchmark result.")


if __name__ == "__main__":
    main()
