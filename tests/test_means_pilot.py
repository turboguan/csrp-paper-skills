import json
from pathlib import Path

from csrp_skills.pilot import load_means_pilot

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "benchmark" / "v0.6" / "means_pilot_questions_v1.json"


def test_means_pilot_has_18_unique_questions():
    suite = load_means_pilot(SUITE_PATH)
    assert len(suite.questions) == 18
    assert len({q.query_id for q in suite.questions}) == 18


def test_means_pilot_complexity_distribution_is_prespecified():
    suite = load_means_pilot(SUITE_PATH)
    counts = {}
    for q in suite.questions:
        counts[q.complexity] = counts.get(q.complexity, 0) + 1
    assert counts == {"low": 5, "medium": 6, "high": 5, "adversarial": 2}


def test_pilot_uses_only_four_frozen_means_papers():
    suite = load_means_pilot(SUITE_PATH)
    allowed = set(suite.corpus_paper_ids)
    assert allowed == {"CSRP-REAL-004", "V03-MEANS-002", "V03-MEANS-003", "V03-MEANS-004"}
    for q in suite.questions:
        assert set(q.required_paper_ids).issubset(allowed)


def test_all_required_claim_ids_exist_in_four_paper_corpus():
    suite = load_means_pilot(SUITE_PATH)
    paths = [
        ROOT / "real_skills" / "CSRP-REAL-004.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        ROOT / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]
    valid = set()
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        valid.update(claim["claim_id"] for claim in data["evidence_claims"])
    required = {cid for q in suite.questions for cid in q.required_claim_ids}
    assert required.issubset(valid)


def test_adversarial_questions_require_no_evidence():
    suite = load_means_pilot(SUITE_PATH)
    adversarial = [q for q in suite.questions if q.complexity == "adversarial"]
    assert len(adversarial) == 2
    assert all(q.expected_mode == "no_evidence" for q in adversarial)
    assert all(not q.required_paper_ids and not q.required_claim_ids for q in adversarial)


def test_no_gold_relation_labels_are_embedded_in_pilot_questions():
    raw = SUITE_PATH.read_text(encoding="utf-8")
    for label in ['"SUPPORTS"', '"CONTRADICTS"', '"QUALIFIES"', '"NOT_COMPARABLE"', '"UNRELATED"']:
        assert label not in raw
