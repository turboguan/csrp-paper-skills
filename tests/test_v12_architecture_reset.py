import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "benchmark" / "v1.2"


def test_active_architecture_order_is_functional_minimal_shared():
    data = json.loads((BASE / "architecture_comparison_v2.json").read_text(encoding="utf-8"))
    assert [item["id"] for item in data["architectures"]] == [
        "functional_multi_agent",
        "minimal_virtual_csrp",
        "shared_knowledge_umbrella",
    ]


def test_paper_agent_committee_is_not_in_active_three_way_comparison():
    data = json.loads((BASE / "architecture_comparison_v2.json").read_text(encoding="utf-8"))
    active = {item["id"] for item in data["architectures"]}
    assert "paper_agent_committee" not in active
    assert "Paper-Agent Committee" in data["historical_note"]


def test_v2_mini_pilot_is_36_cells_with_new_architecture_2():
    data = json.loads((BASE / "MINI_PILOT_36CELL_V2.json").read_text(encoding="utf-8"))
    assert len(data["questions"]) == 6
    assert data["replicates_per_architecture_query"] == 2
    assert data["expected_cells"] == 36
    assert data["architectures"][1] == "minimal_virtual_csrp"
    assert data["architecture_change"]["previous_architecture_2"] == "paper_agent_committee"


def test_v2_theory_matches_specialization_gradient():
    data = json.loads((BASE / "THEORY_HYPOTHESES_V2.json").read_text(encoding="utf-8"))
    assert data["architectures"] == [
        "functional_multi_agent",
        "minimal_virtual_csrp",
        "shared_knowledge_umbrella",
    ]
    levels = {item["architecture"]: item["specialization"] for item in data["conceptual_axis"]}
    assert levels["functional_multi_agent"] == "high"
    assert levels["minimal_virtual_csrp"] == "moderate"
    assert levels["shared_knowledge_umbrella"] == "low"
