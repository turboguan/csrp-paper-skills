from csrp_skills.adjudication import review_row_to_record


BASE = {
    "pair_id": "p1",
    "claim_a": "a",
    "claim_b": "b",
    "reviewer_1_label": "",
    "reviewer_1_rationale": "",
    "reviewer_2_label": "",
    "reviewer_2_rationale": "",
    "adjudicated_label": "",
    "adjudicator_id": "",
    "adjudication_rationale": "",
}


def test_empty_review_row_stays_candidate():
    r = review_row_to_record(dict(BASE), "f")
    assert r.status.value == "candidate"
    assert r.relation is None


def test_unanimous_independent_review_becomes_adjudicated():
    row = dict(BASE)
    row["reviewer_1_label"] = "QUALIFIES"
    row["reviewer_2_label"] = "QUALIFIES"
    row["reviewer_1_rationale"] = "same intervention, different follow-up"
    r = review_row_to_record(row, "f")
    assert r.status.value == "adjudicated"
    assert r.relation.value == "QUALIFIES"
    assert len(r.reviewer_labels) == 2


def test_disagreement_without_adjudicator_is_not_gold():
    row = dict(BASE)
    row["reviewer_1_label"] = "QUALIFIES"
    row["reviewer_2_label"] = "CONTRADICTS"
    r = review_row_to_record(row, "f")
    assert r.status.value == "double_reviewed"
    assert r.relation is None


def test_disagreement_can_be_resolved_by_adjudicator():
    row = dict(BASE)
    row["reviewer_1_label"] = "QUALIFIES"
    row["reviewer_2_label"] = "CONTRADICTS"
    row["adjudicated_label"] = "QUALIFIES"
    row["adjudicator_id"] = "adjudicator-1"
    row["adjudication_rationale"] = "timeframe changes the estimand"
    r = review_row_to_record(row, "f")
    assert r.status.value == "adjudicated"
    assert r.relation.value == "QUALIFIES"
    assert r.adjudicator_id == "adjudicator-1"
