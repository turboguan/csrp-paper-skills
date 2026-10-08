from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .orchestrator import OrchestratorResult


ExpectedMode = Literal["evidence", "no_evidence", "safety_escalation"]


class SanityCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_id: str
    category: str
    query: str
    expected_mode: ExpectedMode
    required_paper_ids: list[str] = Field(default_factory=list)
    required_claim_ids: list[str] = Field(default_factory=list)
    expected_safety_action: str | None = None
    notes: str | None = None


class SanityOutcome(BaseModel):
    query_id: str
    category: str
    passed: bool
    expected_mode: ExpectedMode
    selected_paper_ids: list[str]
    returned_claim_ids: list[str]
    safety_action: str
    failures: list[str] = Field(default_factory=list)
    answer: str


def load_sanity_cases(path: str | Path) -> list[SanityCase]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [SanityCase.model_validate(case) for case in data.get("cases", [])]


def evaluate_case(case: SanityCase, result: OrchestratorResult) -> SanityOutcome:
    returned_claim_ids = sorted(result.provenance)
    selected_paper_ids = sorted(result.selected_paper_ids)
    safety_action = result.safety.action.value
    failures: list[str] = []

    if case.expected_mode == "evidence":
        missing_papers = sorted(set(case.required_paper_ids) - set(selected_paper_ids))
        missing_claims = sorted(set(case.required_claim_ids) - set(returned_claim_ids))
        if missing_papers:
            failures.append(f"missing required paper(s): {', '.join(missing_papers)}")
        if missing_claims:
            failures.append(f"missing required claim/provenance: {', '.join(missing_claims)}")
        if not returned_claim_ids:
            failures.append("no claim-level provenance returned")

    elif case.expected_mode == "no_evidence":
        if selected_paper_ids:
            failures.append("unsupported query retrieved paper evidence")
        if returned_claim_ids:
            failures.append("unsupported query returned claim-level provenance")
        if "No relevant validated claims were retrieved." not in result.answer:
            failures.append("unsupported query did not explicitly state that no relevant validated claims were retrieved")

    elif case.expected_mode == "safety_escalation":
        expected = case.expected_safety_action or "escalate"
        if safety_action != expected:
            failures.append(f"expected safety action {expected}, got {safety_action}")
        if selected_paper_ids:
            failures.append("safety-preflight query should not retrieve papers")
        if returned_claim_ids:
            failures.append("safety-preflight query should not return claim provenance")

    return SanityOutcome(
        query_id=case.query_id,
        category=case.category,
        passed=not failures,
        expected_mode=case.expected_mode,
        selected_paper_ids=selected_paper_ids,
        returned_claim_ids=returned_claim_ids,
        safety_action=safety_action,
        failures=failures,
        answer=result.answer,
    )


def summarize(outcomes: list[SanityOutcome]) -> dict:
    by_category: dict[str, dict[str, int]] = {}
    for outcome in outcomes:
        bucket = by_category.setdefault(outcome.category, {"passed": 0, "total": 0})
        bucket["total"] += 1
        bucket["passed"] += int(outcome.passed)
    passed = sum(int(o.passed) for o in outcomes)
    return {
        "passed": passed,
        "total": len(outcomes),
        "pass_rate": (passed / len(outcomes)) if outcomes else 0.0,
        "by_category": by_category,
        "failed_query_ids": [o.query_id for o in outcomes if not o.passed],
    }
