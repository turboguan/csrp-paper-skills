from pathlib import Path

import pytest

from csrp_skills.benchmark import (
    AdjudicationStatus,
    ClaimPairGold,
    RelationLabel,
    RelationPrediction,
    score_relations,
    validate_candidate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_candidate_manifest_has_three_families_and_unique_dois():
    summary = validate_candidate_manifest(ROOT / "benchmark" / "v0.3" / "candidate_papers.json")
    assert summary["n_papers"] >= 10
    assert len(summary["family_counts"]) == 3
    assert min(summary["family_counts"].values()) >= 3


def test_non_adjudicated_records_are_not_scored_as_gold():
    records = [
        ClaimPairGold(
            pair_id="p1",
            family_id="f",
            claim_a="a",
            claim_b="b",
            relation=RelationLabel.SUPPORTS,
            status=AdjudicationStatus.SINGLE_REVIEWER,
        )
    ]
    result = score_relations(records, [])
    assert result.n == 0
    assert result.ignored_non_gold_ids == ["p1"]


def test_adjudicated_relation_requires_two_reviewers_and_rationale():
    with pytest.raises(ValueError):
        ClaimPairGold(
            pair_id="p1",
            family_id="f",
            claim_a="a",
            claim_b="b",
            relation=RelationLabel.SUPPORTS,
            status=AdjudicationStatus.ADJUDICATED,
            reviewer_ids=["r1"],
            rationale="same population and outcome",
        )


def test_relation_scoring():
    gold = [
        ClaimPairGold(
            pair_id="p1",
            family_id="f",
            claim_a="a1",
            claim_b="b1",
            relation=RelationLabel.QUALIFIES,
            status=AdjudicationStatus.ADJUDICATED,
            reviewer_ids=["r1", "r2"],
            rationale="same intervention but different follow-up window",
        ),
        ClaimPairGold(
            pair_id="p2",
            family_id="f",
            claim_a="a2",
            claim_b="b2",
            relation=RelationLabel.NOT_COMPARABLE,
            status=AdjudicationStatus.ADJUDICATED,
            reviewer_ids=["r1", "r2"],
            rationale="different outcome construct",
        ),
    ]
    preds = [
        RelationPrediction(pair_id="p1", predicted_relation=RelationLabel.QUALIFIES),
        RelationPrediction(pair_id="p2", predicted_relation=RelationLabel.UNRELATED),
    ]
    result = score_relations(gold, preds)
    assert result.n == 2
    assert result.accuracy == 0.5
    assert result.per_label_recall["QUALIFIES"] == 1.0
    assert result.per_label_recall["NOT_COMPARABLE"] == 0.0
