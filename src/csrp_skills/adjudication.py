from __future__ import annotations

import csv
from pathlib import Path

from .benchmark import AdjudicationStatus, ClaimPairGold, RelationLabel


def _label(value: str | None) -> RelationLabel | None:
    value = (value or "").strip()
    return RelationLabel(value) if value else None


def review_row_to_record(row: dict[str, str], family_id: str) -> ClaimPairGold:
    r1 = _label(row.get("reviewer_1_label"))
    r2 = _label(row.get("reviewer_2_label"))
    adjudicated = _label(row.get("adjudicated_label"))
    reviewer_labels: dict[str, RelationLabel] = {}

    if r1:
        reviewer_labels["reviewer_1"] = r1
    if r2:
        reviewer_labels["reviewer_2"] = r2

    if not r1 and not r2:
        status = AdjudicationStatus.CANDIDATE
        final = None
        rationale = None
    elif bool(r1) ^ bool(r2):
        status = AdjudicationStatus.SINGLE_REVIEWER
        final = None
        rationale = None
    elif r1 == r2:
        status = AdjudicationStatus.ADJUDICATED
        final = r1
        rationale = (
            row.get("adjudication_rationale")
            or row.get("reviewer_1_rationale")
            or row.get("reviewer_2_rationale")
            or "Independent reviewers agreed."
        )
    elif adjudicated and row.get("adjudicator_id", "").strip():
        status = AdjudicationStatus.ADJUDICATED
        final = adjudicated
        rationale = row.get("adjudication_rationale") or "Reviewer disagreement resolved by adjudication."
    else:
        status = AdjudicationStatus.DOUBLE_REVIEWED
        final = None
        rationale = None

    return ClaimPairGold(
        pair_id=row["pair_id"],
        family_id=family_id,
        claim_a=row["claim_a"],
        claim_b=row["claim_b"],
        relation=final,
        status=status,
        rationale=rationale,
        reviewer_ids=list(reviewer_labels),
        reviewer_labels=reviewer_labels,
        adjudicator_id=(row.get("adjudicator_id") or "").strip() or None,
        notes=["Generated from blinded review sheet."],
    )


def build_gold_from_csv(path: str | Path, family_id: str) -> list[ClaimPairGold]:
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [review_row_to_record(row, family_id=family_id) for row in rows]
