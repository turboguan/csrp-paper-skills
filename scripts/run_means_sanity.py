from __future__ import annotations

import json
from pathlib import Path

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry
from csrp_skills.sanity import evaluate_case, load_sanity_cases, summarize


def build_means_system(root: Path) -> Orchestrator:
    factory = PaperToSkillFactory()
    registry = SkillRegistry()
    paths = [
        root / "real_skills" / "CSRP-REAL-004.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-002.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-003.json",
        root / "real_skills" / "v0.3" / "V03-MEANS-004.json",
    ]
    for path in paths:
        registry.register(factory.from_json(path))
    return Orchestrator(registry, EvidenceGraph().build_graph(registry.all()))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    suite_path = root / "benchmark" / "v0.3" / "sanity" / "means_sanity_queries_v1.json"
    cases = load_sanity_cases(suite_path)
    system = build_means_system(root)

    outcomes = [evaluate_case(case, system.run(case.query)) for case in cases]
    summary = summarize(outcomes)

    out_dir = root / "outputs" / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "means_sanity_v1.json"
    md_path = out_dir / "means_sanity_v1.md"

    payload = {
        "suite_id": "means_sanity_v1",
        "system": "paper_as_skill_deterministic_v0.3",
        "scientific_status": "engineering_sanity_test_not_benchmark_result",
        "summary": summary,
        "outcomes": [o.model_dump() for o in outcomes],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Means Sanity v1",
        "",
        "**Status:** engineering sanity test; not a scientific benchmark result.",
        "",
        f"Passed: **{summary['passed']} / {summary['total']}**",
        "",
        "| Query | Category | Result | Failure |",
        "|---|---|---|---|",
    ]
    for outcome in outcomes:
        failure = "; ".join(outcome.failures) if outcome.failures else ""
        lines.append(
            f"| {outcome.query_id} | {outcome.category} | {'PASS' if outcome.passed else 'FAIL'} | {failure} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(json_path)
    print(md_path)
    print("NOTE: relation-label correctness is deliberately not scored before Human Gold adjudication.")


if __name__ == "__main__":
    main()
