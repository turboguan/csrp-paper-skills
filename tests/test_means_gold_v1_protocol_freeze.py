from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "benchmark" / "v0.3" / "frozen" / "means_restriction_gold_v1"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _read_csv(name: str):
    with (FREEZE / name).open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_frozen_corpus_manifest_matches_exact_paper_skill_blobs():
    manifest = json.loads((FREEZE / "corpus_manifest.json").read_text(encoding="utf-8"))
    assert manifest["freeze_version"] == "means-gold-v1.0"
    assert manifest["paper_count"] == 4
    assert manifest["claim_count"] == 9

    for paper in manifest["papers"]:
        path = ROOT / paper["paper_skill_path"]
        assert path.exists()
        assert _git_blob_sha(path) == paper["paper_skill_git_blob_sha"]


def test_claim_review_sheets_are_identical_and_blank():
    a = _read_csv("reviewer_A_claim_provenance.csv")
    b = _read_csv("reviewer_B_claim_provenance.csv")
    assert a == b
    assert len(a) == 9

    review_fields = [
        "claim_verdict",
        "provenance_verdict",
        "direction_verdict",
        "causal_language_verdict",
        "population_fidelity",
        "intervention_fidelity",
        "outcome_fidelity",
        "method_fidelity",
        "proposed_claim_text",
        "proposed_provenance_locator",
        "reviewer_comments",
    ]
    assert all(not row[field].strip() for row in a for field in review_fields)


def test_relation_review_sheets_are_blinded_and_blank():
    a = _read_csv("reviewer_A_relations.csv")
    b = _read_csv("reviewer_B_relations.csv")
    assert a == b
    assert len(a) == 4
    assert {row["pair_id"] for row in a} == {"MEANS-P01", "MEANS-P02", "MEANS-P03", "MEANS-P04"}

    forbidden_columns = {"model_suggested_relation", "gold_relation", "adjudicated_label"}
    assert forbidden_columns.isdisjoint(a[0].keys())

    reviewer_fields = [
        "population_comparability",
        "intervention_or_exposure_comparability",
        "outcome_comparability",
        "method_or_estimand_comparability",
        "timeframe_comparability",
        "dataset_or_programme_dependency",
        "relation_label",
        "confidence",
        "rationale",
        "source_verified",
        "reviewer_comments",
    ]
    assert all(not row[field].strip() for row in a for field in reviewer_fields)


def test_analysis_plan_freezes_primary_contrast_and_pilot_rule():
    config = json.loads((FREEZE / "analysis_config.json").read_text(encoding="utf-8"))
    assert config["primary_contrast"] == ["paper_as_skill", "one_paper_one_agent"]
    assert config["primary_endpoint_full_benchmark"] == "cross_paper_relation_accuracy"
    assert config["pilot_relation_pairs"] == 4
    assert config["pilot_is_confirmatory"] is False
    assert config["bootstrap_resamples"] == 10000
    assert config["pilot_inference_rule"] == "descriptive_only_no_confirmatory_superiority_claim"


def test_adjudication_master_contains_no_prefilled_gold_labels():
    rows = _read_csv("relation_adjudication_master.csv")
    assert len(rows) == 4
    assert all(not row["adjudicated_label"].strip() for row in rows)
    assert all(not row["final_status"].strip() for row in rows)
