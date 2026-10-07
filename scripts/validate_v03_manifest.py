from pathlib import Path

from csrp_skills.benchmark import load_claim_pairs, validate_candidate_manifest


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "benchmark" / "v0.3" / "candidate_papers.json"
    pairs = root / "benchmark" / "v0.3" / "means_restriction_candidate_pairs.jsonl"
    print(validate_candidate_manifest(manifest))
    records = load_claim_pairs(pairs)
    print({"candidate_pairs": len(records), "gold_pairs": sum(r.relation is not None for r in records)})


if __name__ == "__main__":
    main()
