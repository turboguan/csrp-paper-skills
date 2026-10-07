from __future__ import annotations

from dataclasses import dataclass

from .models import EvidenceClaim, PaperSkill


_CLAIM_STOPWORDS = {
    "what", "does", "about", "from", "with", "these", "those", "based", "evidence", "study", "studies",
    "paper", "papers", "findings", "result", "results", "the", "and", "for", "are", "was", "were", "have",
    "has", "how", "can", "could", "would", "should", "into", "this", "that", "available", "across", "in",
    "of", "to", "a", "an", "on", "did", "do", "say", "suggest", "csrp", "population", "level", "prevention",
    "strategy", "strategies", "represented", "types", "type",
}


def _query_terms(query: str) -> list[str]:
    terms: list[str] = []
    for raw in query.replace("/", " ").replace("-", " ").split():
        term = raw.casefold().strip("?,.;:()[]{}\"'")
        if len(term) >= 3 and term not in _CLAIM_STOPWORDS:
            terms.append(term)
    return terms


@dataclass
class EvidenceWorkspace:
    query: str
    skills: list[PaperSkill]

    @property
    def all_claims(self) -> list[EvidenceClaim]:
        return [claim for skill in self.skills for claim in skill.evidence_claims]

    @property
    def claims(self) -> list[EvidenceClaim]:
        claims = self.all_claims
        terms = _query_terms(self.query)
        if not claims or not terms:
            return claims
        scored: list[tuple[int, EvidenceClaim]] = []
        for claim in claims:
            text = " ".join(
                [claim.claim_id, claim.statement, claim.population or "", claim.intervention_or_exposure or "", claim.outcome or "", claim.method or ""]
            ).casefold()
            score = sum(text.count(t) for t in terms)
            if score:
                scored.append((score, claim))
        if not scored:
            return claims
        best = max(score for score, _ in scored)
        threshold = max(1, int(best * 0.5))
        return [claim for score, claim in scored if score >= threshold]


@dataclass
class AgentDraft:
    role: str
    text: str
    claim_ids: list[str]


class DomainAgent:
    def __init__(self, role: str):
        self.role = role

    def reason(self, workspace: EvidenceWorkspace) -> AgentDraft:
        claims = workspace.claims
        if not claims:
            return AgentDraft(self.role, "No relevant validated claims were retrieved.", [])
        lines = [f"{self.role} shared-workspace synthesis from {len(workspace.skills)} paper skill(s):"]
        for c in claims:
            lines.append(f"- [{c.claim_id}] {c.statement}")
        return AgentDraft(self.role, "\n".join(lines), [c.claim_id for c in claims])
