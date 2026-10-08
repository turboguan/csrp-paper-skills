from pathlib import Path

from csrp_skills.sanity import load_sanity_cases

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmark" / "v0.3" / "sanity" / "means_sanity_queries_v1.json"


def test_sanity_suite_has_15_prespecified_cases():
    cases = load_sanity_cases(SUITE)
    assert len(cases) == 15
    assert len({case.query_id for case in cases}) == 15


def test_sanity_suite_covers_evidence_unsupported_hard_negative_and_safety():
    cases = load_sanity_cases(SUITE)
    categories = {case.category for case in cases}
    assert "single_paper_factual" in categories
    assert "cross_paper_evidence" in categories
    assert "unsupported_off_topic" in categories
    assert "hard_negative" in categories
    assert "safety_boundary" in categories


def test_no_relation_gold_is_embedded_in_sanity_suite():
    raw = SUITE.read_text(encoding="utf-8")
    for forbidden in ['"SUPPORTS"', '"CONTRADICTS"', '"QUALIFIES"', '"NOT_COMPARABLE"', '"UNRELATED"']:
        assert forbidden not in raw


def test_unsupported_cases_require_no_papers_or_claims():
    cases = load_sanity_cases(SUITE)
    negatives = [case for case in cases if case.expected_mode == "no_evidence"]
    assert len(negatives) >= 5
    assert all(not case.required_paper_ids for case in negatives)
    assert all(not case.required_claim_ids for case in negatives)
