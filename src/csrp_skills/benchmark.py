from __future__ import annotations

import json
from collections import Counter, defaultdict
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RelationLabel(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    QUALIFIES = "QUALIFIES"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    UNRELATED = "UNRELATED"


class AdjudicationStatus(str, Enum):
    CANDIDATE = "candidate"
    SINGLE_REVIEWER = "single_reviewer"
    DOUBLE_REVIEWED = "double_reviewed"
    ADJUDICATED = "adjudicated"


class ClaimPairGold(BaseModel):
    """Candidate or gold relation between two evidence claims.

    The gold relation remains null until human review is complete. A model may
    store a suggestion for triage, but that suggestion is never scored as gold.
    """

    model_config = ConfigDict(extra="forbid")

    pair_id: str
    family_id: str
    claim_a: str
    claim_b: str
    relation: RelationLabel | None = None
    status: AdjudicationStatus = AdjudicationStatus.CANDIDATE
    rationale: str | None = None
    rationale_for_review: str | None = None
    dimensions: dict[str, str] = Field(default_factory=dict)
    reviewer_ids: list[str] = Field(default_factory=list)
    reviewer_labels: dict[str, RelationLabel] = Field(default_factory=dict)
    adjudicator_id: str | None = None
    model_suggested_relation: RelationLabel | None = None
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_adjudication_state(self):
        if self.claim_a == self.claim_b:
            raise ValueError("claim_a and claim_b must be different")

        reviewers = set(self.reviewer_ids) | set(self.reviewer_labels)
        if self.status == AdjudicationStatus.ADJUDICATED:
            if self.relation is None:
                raise ValueError("adjudicated relation requires a relation label")
            if not self.rationale:
                raise ValueError("adjudicated relation requires a rationale")
            if len(reviewers) < 2:
                raise ValueError("adjudicated relation requires at least two reviewers")
            if self.reviewer_labels:
                labels = set(self.reviewer_labels.values())
                if len(labels) == 1 and self.relation not in labels:
                    raise ValueError("adjudicated relation must match unanimous reviewer labels")
                if len(labels) > 1 and not self.adjudicator_id:
                    raise ValueError("disagreeing reviewer labels require an adjudicator_id")
        return self


class RelationPrediction(BaseModel):
    pair_id: str
    predicted_relation: RelationLabel
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    explanation: str | None = None


class RelationScore(BaseModel):
    n: int
    accuracy: float
    per_label_recall: dict[str, float]
    confusion: dict[str, dict[str, int]]
    missing_prediction_ids: list[str]
    ignored_non_gold_ids: list[str]


def load_claim_pairs(path: str | Path) -> list[ClaimPairGold]:
    path = Path(path)
    records: list[ClaimPairGold] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(ClaimPairGold.model_validate_json(line))
            except Exception as exc:
                raise ValueError(f"invalid relation record at {path}:{line_no}: {exc}") from exc
    return records


def score_relations(gold_records: list[ClaimPairGold], predictions: list[RelationPrediction]) -> RelationScore:
    """Score only adjudicated records.

    Candidate, model-suggested and single-reviewer labels are explicitly ignored.
    """
    gold = {r.pair_id: r for r in gold_records if r.status == AdjudicationStatus.ADJUDICATED}
    ignored = [r.pair_id for r in gold_records if r.status != AdjudicationStatus.ADJUDICATED]
    pred = {p.pair_id: p for p in predictions}

    if not gold:
        return RelationScore(
            n=0,
            accuracy=0.0,
            per_label_recall={},
            confusion={},
            missing_prediction_ids=[],
            ignored_non_gold_ids=sorted(ignored),
        )

    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    correct = 0
    missing: list[str] = []

    for pair_id, record in gold.items():
        assert record.relation is not None
        if pair_id not in pred:
            missing.append(pair_id)
            continue
        predicted = pred[pair_id].predicted_relation
        confusion[record.relation.value][predicted.value] += 1
        if predicted == record.relation:
            correct += 1

    per_label_recall: dict[str, float] = {}
    for label in RelationLabel:
        support = sum(confusion[label.value].values())
        if support:
            per_label_recall[label.value] = confusion[label.value][label.value] / support

    return RelationScore(
        n=len(gold),
        accuracy=correct / len(gold),
        per_label_recall=per_label_recall,
        confusion={truth: dict(counts) for truth, counts in confusion.items()},
        missing_prediction_ids=sorted(missing),
        ignored_non_gold_ids=sorted(ignored),
    )


def validate_candidate_manifest(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    papers = data.get("papers", [])
    ids = [p["candidate_id"] for p in papers]
    dois = [p.get("doi") for p in papers if p.get("doi")]
    families = Counter(p["family_id"] for p in papers)

    if len(ids) != len(set(ids)):
        raise ValueError("candidate_id values must be unique")
    if len(dois) != len(set(dois)):
        raise ValueError("DOIs must be unique in the candidate manifest")
    if any(count < 3 for count in families.values()):
        raise ValueError("each evidence family must have at least three candidate papers")

    return {
        "n_papers": len(papers),
        "family_counts": dict(families),
        "n_unique_dois": len(set(dois)),
    }
