from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import EvidenceClaim


class SafetyAction(str, Enum):
    allow = "allow"
    revise = "revise"
    abstain = "abstain"
    escalate = "escalate"


@dataclass
class SafetyResult:
    action: SafetyAction
    reasons: list[str] = field(default_factory=list)
    safe_message: str | None = None


class SafetySupervisor:
    individual_risk_patterns = (
        "suicide risk percentage",
        "my suicide risk",
        "predict my risk",
        "individual risk score",
        "probability i will",
        "chance i will die by suicide",
    )
    clinical_action_patterns = (
        "should i stop medication",
        "what drug should i take",
        "diagnose me",
        "should this patient be discharged",
    )

    def review(self, query: str, draft: str, claims: list[EvidenceClaim]) -> SafetyResult:
        q = query.casefold()
        if any(p in q for p in self.individual_risk_patterns):
            return SafetyResult(
                SafetyAction.escalate,
                ["individual suicide-risk scoring is outside the evidence-system scope"],
                "This research prototype does not calculate or classify an individual's suicide risk. Individual-level safety concerns require an appropriate qualified human/professional pathway rather than inference from population studies.",
            )
        if any(p in q for p in self.clinical_action_patterns):
            return SafetyResult(
                SafetyAction.escalate,
                ["requested individualized clinical action is outside scope"],
                "This prototype is designed for evidence synthesis, not individualized diagnosis, treatment, medication, discharge, or emergency decision-making.",
            )
        reasons = []
        if claims and not all(c.provenance for c in claims):
            reasons.append("one or more claims lack provenance")
        noncausal = [c for c in claims if not c.causal_language_allowed]
        if noncausal and any(word in draft.casefold() for word in [" causes ", " proves ", " guarantees "]):
            reasons.append("draft uses causal language not permitted by source claim metadata")
        if reasons:
            return SafetyResult(SafetyAction.revise, reasons)
        return SafetyResult(SafetyAction.allow)
