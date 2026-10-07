import json
from pathlib import Path

from csrp_skills.benchmark import load_claim_pairs
from csrp_skills.factory import PaperToSkillFactory

ROOT = Path(__file__).resolve().parents[1]


def test_v03_means_candidate_skills_validate():
    factory = PaperToSkillFactory()
    paths = sorted((ROOT / "real_skills" / "v0.3").glob("V03-MEANS-*.json"))
    assert len(paths) == 3
    skills = [factory.from_json(path) for path in paths]
    assert all(s.metadata["human_validation_status"] == "model_curated_not_expert_validated" for s in skills)


def test_v03_candidate_pairs_are_not_gold():
    records = load_claim_pairs(ROOT / "benchmark" / "v0.3" / "means_restriction_candidate_pairs.jsonl")
    assert len(records) == 4
    assert all(record.relation is None for record in records)
    assert all(record.status.value == "candidate" for record in records)


def test_v03_candidate_pairs_expose_comparability_dimensions():
    records = load_claim_pairs(ROOT / "benchmark" / "v0.3" / "means_restriction_candidate_pairs.jsonl")
    required = {"population", "intervention_or_exposure", "outcome", "method", "timeframe", "dataset_dependency"}
    assert all(required.issubset(record.dimensions) for record in records)
