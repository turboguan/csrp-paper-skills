from __future__ import annotations

import re
from dataclasses import dataclass

from .models import PaperSkill


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_EFFECT_MARKERS = (
    "improve", "improves", "improved",
    "reduce", "reduces", "reduced",
    "increase", "increases", "increased",
    "effect on", "effects on", "impact on",
)
_GENERIC_TAIL_TERMS = {
    "the", "a", "an", "this", "that", "these", "those", "intervention", "study", "studies",
    "paper", "papers", "outcome", "outcomes", "effect", "effects", "suicide", "rate", "rates",
    "risk", "population", "people", "during", "after", "before", "long", "term", "short",
}


@dataclass(frozen=True)
class SupportGateResult:
    supported: bool
    reason: str


class EvidenceSupportGate:
    """Conservative lexical support gate for the deterministic MVP.

    It is intentionally narrow. It catches a common hard-negative failure mode:
    the query shares the intervention/topic with retrieved papers but asks for an
    outcome that does not exist in the retrieved evidence.

    This is not a semantic entailment model. The matched LLM benchmark should
    replace or supplement it with a fixed retriever/evidence-sufficiency module.
    """

    def review(self, query: str, skills: list[PaperSkill]) -> SupportGateResult:
        if not skills:
            return SupportGateResult(False, "no paper skill was retrieved")

        q = query.casefold()
        marker = next((m for m in _EFFECT_MARKERS if m in q), None)
        if marker is None:
            return SupportGateResult(True, "no explicit effect-target phrase detected")

        tail = q.split(marker, 1)[1]
        tail_terms = [
            token for token in _TOKEN_RE.findall(tail)
            if len(token) >= 4 and token not in _GENERIC_TAIL_TERMS
        ]
        if not tail_terms:
            return SupportGateResult(True, "effect target contains no specific lexical term")

        evidence_text = " ".join(
            [
                *[outcome for skill in skills for outcome in skill.outcomes],
                *[claim.statement for skill in skills for claim in skill.evidence_claims],
            ]
        ).casefold()

        matched = [term for term in tail_terms if term in evidence_text]
        if not matched:
            return SupportGateResult(
                False,
                "query asks for an effect target not represented in retrieved outcomes/claims",
            )

        return SupportGateResult(True, "effect target is represented in retrieved evidence")
