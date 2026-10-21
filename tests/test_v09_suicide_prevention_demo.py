import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "benchmark" / "v0.9" / "suicide_prevention_llm_demo_v1.json"


def test_v09_demo_has_five_paper_corpus_and_six_questions():
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert len(data["corpus_paper_ids"]) == 5
    assert len(data["questions"]) == 6
    assert data["model_id"] == "gpt-6.1-sol"


def test_v09_demo_remains_suicide_prevention_focused():
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    themes = {item["theme"] for item in data["questions"]}
    assert {
        "school_youth_prevention",
        "surveillance_epidemiology",
        "postdischarge_support",
        "means_restriction",
        "media_reporting",
        "cross_domain_synthesis",
    } == themes


def test_v09_demo_does_not_claim_full_corpus_or_benchmark():
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    text = " ".join(data["interpretation_boundary"]).casefold()
    assert "not a scientific benchmark" in text
    assert "do not represent the full csrp corpus" in text
    assert "no autonomous individual suicide-risk scoring" in text
