from __future__ import annotations

import re

from .models import EvidenceClaim, PaperSkill


_CLAIM_ID_RE = re.compile(r"(?:SYN-\d{3}-C\d+|CSRP-REAL-\d{3}-C\d+|V03-[A-Z]+-\d{3}-C\d+)")


def render_paper_skill(skill: PaperSkill) -> str:
    lines = [
        f"PAPER_ID: {skill.paper_id}",
        f"TITLE: {skill.title}",
        f"STUDY_TYPE: {skill.study_type}",
        f"POPULATION: {' | '.join(skill.population)}",
        f"INTERVENTION_OR_EXPOSURE: {' | '.join(skill.intervention_or_exposure)}",
        f"OUTCOMES: {' | '.join(skill.outcomes)}",
        "CLAIMS:",
    ]
    for claim in skill.evidence_claims:
        lines.append(f"[{claim.claim_id}] {claim.statement}")
    if skill.limitations:
        lines.append("LIMITATIONS: " + " | ".join(skill.limitations))
    if skill.applicability:
        lines.append("APPLICABILITY: " + " | ".join(skill.applicability))
    return "\n".join(lines)


def render_evidence(skills: list[PaperSkill] | tuple[PaperSkill, ...]) -> str:
    return "\n\n---\n\n".join(render_paper_skill(skill) for skill in skills)


def extract_claim_ids(text: str) -> list[str]:
    seen = []
    for claim_id in _CLAIM_ID_RE.findall(text):
        if claim_id not in seen:
            seen.append(claim_id)
    return seen


def claims_by_id(skills: list[PaperSkill] | tuple[PaperSkill, ...]) -> dict[str, EvidenceClaim]:
    return {claim.claim_id: claim for skill in skills for claim in skill.evidence_claims}
