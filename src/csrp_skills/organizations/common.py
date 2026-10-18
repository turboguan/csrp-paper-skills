from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from ..agents import EvidenceWorkspace
from ..models import EvidenceClaim, PaperSkill
from ..registry import SkillRegistry
from ..support import EvidenceSupportGate


@dataclass
class OrganizationMessage:
    actor: str
    role: str
    content: str
    paper_ids: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)


@dataclass
class OrganizationResult:
    architecture: str
    query: str
    answer: str
    selected_paper_ids: list[str]
    provenance: dict[str, list[dict[str, Any]]]
    transcript: list[OrganizationMessage]
    metrics: dict[str, Any]
    experimental_status: str = "deterministic_architecture_scaffold_not_llm_benchmark"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


class BaseEvidenceOrganization:
    """Shared retrieval and provenance plumbing for organization-design experiments.

    The three organizational architectures must see the same evidence substrate.
    Architecture-specific code should change coordination and context structure,
    not silently change the corpus.
    """

    architecture_name: str

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.support_gate = EvidenceSupportGate()

    def retrieve(self, query: str, limit: int = 12) -> list[PaperSkill]:
        match = re.search(r"(?:SYN-\d{3}|CSRP-REAL-\d{3}|V03-[A-Z]+-\d{3})", query.upper())
        if match:
            try:
                skills = [self.registry.get(match.group(0))]
            except KeyError:
                skills = []
        else:
            skills = self.registry.keyword_search(query, limit=limit)

        support = self.support_gate.review(query, skills)
        return skills if support.supported else []

    @staticmethod
    def workspace(query: str, skills: list[PaperSkill]) -> EvidenceWorkspace:
        return EvidenceWorkspace(query=query, skills=skills)

    @staticmethod
    def provenance_for_claims(claims: list[EvidenceClaim]) -> dict[str, list[dict[str, Any]]]:
        return {
            claim.claim_id: [p.model_dump() for p in claim.provenance]
            for claim in claims
        }

    def no_evidence_result(self, query: str) -> OrganizationResult:
        return OrganizationResult(
            architecture=self.architecture_name,
            query=query,
            answer="No relevant validated claims were retrieved.",
            selected_paper_ids=[],
            provenance={},
            transcript=[
                OrganizationMessage(
                    actor="EvidenceGate",
                    role="evidence_sufficiency",
                    content="No supported evidence was retrieved; the organization failed closed.",
                )
            ],
            metrics={
                "evidence_count": 0,
                "claim_count": 0,
                "coordination_messages": 1,
                "llm_calls": 0,
            },
        )
