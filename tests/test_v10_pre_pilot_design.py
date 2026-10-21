import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "benchmark" / "prepilot_v1"


def test_pre_pilot_freeze_points_to_v09_source_commit():
    data = json.loads((BASE / "FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    assert data["freeze_id"] == "virtual-csrp-prepilot-v1"
    assert data["source_commit"] == "a736b38af323a0155344e20b1597a33801e381e5"
    assert data["scientific_status"].startswith("pre-pilot")


def test_theory_has_five_directional_hypotheses():
    data = json.loads((BASE / "THEORY_HYPOTHESES_V1.json").read_text(encoding="utf-8"))
    assert [h["id"] for h in data["hypotheses"]] == ["H1", "H2", "H3", "H4", "H5"]
    assert data["primary_theory"] == "Organizational Information Processing Theory"
    assert "Contingency Theory" in data["complementary_theories"]


def test_mini_pilot_is_exactly_36_cells():
    data = json.loads((BASE / "MINI_PILOT_36CELL_V1.json").read_text(encoding="utf-8"))
    assert len(data["questions"]) == 6
    assert len(data["architectures"]) == 3
    assert data["replicates_per_architecture_query"] == 2
    assert data["expected_cells"] == 36
    assert len(data["questions"]) * len(data["architectures"]) * data["replicates_per_architecture_query"] == 36


def test_mini_pilot_spans_task_demands_and_hard_negative():
    data = json.loads((BASE / "MINI_PILOT_36CELL_V1.json").read_text(encoding="utf-8"))
    levels = {q["task_interdependence"] for q in data["questions"]}
    assert {0, 1, 2, 3}.issubset(levels)
    assert any(q["expected_mode"] == "no_evidence" for q in data["questions"])
    assert any(q["task_type"] == "decision_memo" for q in data["questions"])


def test_flagship_is_population_policy_case_not_individual_risk_case():
    data = json.loads((BASE / "FLAGSHIP_CASE_V1.json").read_text(encoding="utf-8"))
    assert data["service_channel"] == "Policy Intelligence"
    assert len(data["corpus_paper_ids"]) == 4
    assert "Population-level" in data["boundary"]
    assert "no individual risk scoring" in data["boundary"]


def test_mini_pilot_uses_only_frozen_means_restriction_corpus():
    data = json.loads((BASE / "MINI_PILOT_36CELL_V1.json").read_text(encoding="utf-8"))
    allowed = set(data["corpus_paper_ids"])
    assert allowed == {"CSRP-REAL-004", "V03-MEANS-002", "V03-MEANS-003", "V03-MEANS-004"}
    for q in data["questions"]:
        assert set(q["required_paper_ids"]).issubset(allowed)
