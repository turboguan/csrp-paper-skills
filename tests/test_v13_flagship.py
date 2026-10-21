import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "benchmark" / "v1.3" / "FLAGSHIP_THREE_ARCHITECTURE_V1.json"


def test_flagship_uses_active_three_architectures_in_order():
    data = json.loads(CFG.read_text(encoding="utf-8"))
    assert data["architectures"] == [
        "functional_multi_agent",
        "minimal_virtual_csrp",
        "shared_knowledge_umbrella",
    ]


def test_flagship_uses_four_paper_means_restriction_corpus():
    data = json.loads(CFG.read_text(encoding="utf-8"))
    assert data["corpus_paper_ids"] == [
        "CSRP-REAL-004",
        "V03-MEANS-002",
        "V03-MEANS-003",
        "V03-MEANS-004",
    ]


def test_flagship_is_diagnostic_and_blinded():
    data = json.loads(CFG.read_text(encoding="utf-8"))
    assert data["evaluation"]["blinded"] is True
    assert "diagnostic" in data["evaluation"]["interpretation"].lower()


def test_flagship_keeps_population_level_safety_boundary():
    data = json.loads(CFG.read_text(encoding="utf-8"))
    boundary = data["safety_boundary"].lower()
    assert "population-level" in boundary
    assert "no individual risk scoring" in boundary


def test_flagship_has_same_model_and_token_controls():
    data = json.loads(CFG.read_text(encoding="utf-8"))
    controls = data["matched_controls"]
    assert controls["evidence_budget_papers"] == 4
    assert controls["max_total_tokens_per_architecture"] == 16000
    assert controls["temperature"] == 0.0
