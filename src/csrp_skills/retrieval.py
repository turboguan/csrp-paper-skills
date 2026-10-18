from __future__ import annotations

import re
from dataclasses import dataclass

from .models import PaperSkill
from .registry import SkillRegistry
from .support import EvidenceSupportGate


@dataclass(frozen=True)
class EvidencePacket:
    query: str
    skills: tuple[PaperSkill, ...]
    retriever_id: str
    evidence_budget: int

    @property
    def paper_ids(self) -> list[str]:
        return [skill.paper_id for skill in self.skills]


class FixedEvidenceRetriever:
    """One fixed retriever used once per query for every architecture.

    Matched experiments retrieve a single EvidencePacket and distribute that
    identical packet to all organizations. This prevents architecture-specific
    retrieval from becoming a hidden treatment.
    """

    retriever_id = "weighted_keyword_v03_plus_support_gate_v1"

    def __init__(self, registry: SkillRegistry, evidence_budget: int):
        self.registry = registry
        self.evidence_budget = evidence_budget
        self.support_gate = EvidenceSupportGate()

    def retrieve(self, query: str) -> EvidencePacket:
        match = re.search(r"(?:SYN-\d{3}|CSRP-REAL-\d{3}|V03-[A-Z]+-\d{3})", query.upper())
        if match:
            try:
                skills = [self.registry.get(match.group(0))]
            except KeyError:
                skills = []
        else:
            skills = self.registry.keyword_search(query, limit=self.evidence_budget)

        support = self.support_gate.review(query, skills)
        if not support.supported:
            skills = []

        skills = skills[: self.evidence_budget]
        return EvidencePacket(
            query=query,
            skills=tuple(skills),
            retriever_id=self.retriever_id,
            evidence_budget=self.evidence_budget,
        )
