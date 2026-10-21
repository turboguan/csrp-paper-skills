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
from csrp_skills.virtual_csrp import VirtualCSRPInstitute


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

    institute = VirtualCSRPInstitute(
        {
            "functional_multi_agent": FunctionalMultiAgentOrganization(registry),
            "paper_agent_committee": PaperAgentCommittee(registry),
            "shared_knowledge_umbrella": SharedKnowledgeOrganization(orchestrator),
        }
    )

    query = (
        "What evidence supports or limits retail charcoal-access restriction, "
        "and what implementation issues matter for policy?"
    )

    print("VIRTUAL CSRP PLAN")
    print(institute.plan(query))
    print()
    for architecture_id in institute.available_architectures():
        result = institute.run(query, architecture_id)
        print(f"=== {architecture_id} ===")
        print(result.answer)
        print()


if __name__ == "__main__":
    main()
