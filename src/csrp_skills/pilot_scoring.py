from __future__ import annotations

from dataclasses import dataclass, asdict

from .evidence_format import extract_claim_ids
from .pilot import PilotQuestion


@dataclass
class AutomatedPilotScore:
    query_id: str
    architecture: str
    paper_recall: float | None
    required_claim_provenance_recall: float | None
    cited_claim_ids: list[str]
    invalid_citation_ids: list[str]
    abstention_correct: bool | None
    llm_calls: int
    total_tokens: int
    coordination_messages: int

    def to_dict(self):
        return asdict(self)


def _recall(required: list[str], observed: list[str]) -> float | None:
    if not required:
        return None
    return len(set(required) & set(observed)) / len(set(required))


def score_pilot_record(question: PilotQuestion, record, valid_claim_ids: set[str]) -> AutomatedPilotScore:
    paper_recall = _recall(question.required_paper_ids, record.selected_paper_ids)
    provenance_claim_ids = list(record.provenance)
    claim_recall = _recall(question.required_claim_ids, provenance_claim_ids)
    cited = extract_claim_ids(record.answer)
    invalid = [claim_id for claim_id in cited if claim_id not in valid_claim_ids]

    abstention_correct = None
    if question.expected_mode == "no_evidence":
        abstention_correct = (
            not record.selected_paper_ids
            and not record.provenance
            and "No relevant validated claims were retrieved." in record.answer
        )

    return AutomatedPilotScore(
        query_id=question.query_id,
        architecture=record.architecture,
        paper_recall=paper_recall,
        required_claim_provenance_recall=claim_recall,
        cited_claim_ids=cited,
        invalid_citation_ids=invalid,
        abstention_correct=abstention_correct,
        llm_calls=int(record.metrics.get("llm_calls", 0)),
        total_tokens=int(record.metrics.get("total_tokens", 0)),
        coordination_messages=int(record.metrics.get("coordination_messages", 0)),
    )
