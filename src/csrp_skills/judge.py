from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum

from .graph import norm
from .models import Direction, EvidenceClaim


class JudgeLabel(str, Enum):
    strongly_consistent = "strongly_consistent"
    moderately_consistent = "moderately_consistent"
    mixed = "mixed"
    insufficient = "insufficient"
    population_mismatch = "population_mismatch"
    methodologically_noncomparable = "methodologically_noncomparable"
    heterogeneous = "heterogeneous"


@dataclass
class JudgeResult:
    label: JudgeLabel
    rationale: str
    supporting_claim_ids: list[str]


class EvidenceJudge:
    def adjudicate(self, claims: list[EvidenceClaim], target_population: str | None = None) -> JudgeResult:
        if not claims:
            return JudgeResult(JudgeLabel.insufficient, "No validated claims were available.", [])
        ids = [c.claim_id for c in claims]
        if target_population:
            matched = [c for c in claims if norm(target_population) in norm(c.population)]
            if not matched:
                return JudgeResult(
                    JudgeLabel.population_mismatch,
                    f"No retrieved claim directly studies target population: {target_population}.",
                    ids,
                )

        comparable_groups: dict[tuple[str, str, str, str], list[EvidenceClaim]] = {}
        for c in claims:
            key = (norm(c.population), norm(c.intervention_or_exposure), norm(c.outcome), norm(c.method))
            comparable_groups.setdefault(key, []).append(c)
        true_conflict_ids: list[str] = []
        for group in comparable_groups.values():
            dirs = {c.direction for c in group}
            if Direction.beneficial in dirs and Direction.harmful in dirs:
                true_conflict_ids.extend(c.claim_id for c in group)
        if true_conflict_ids:
            return JudgeResult(
                JudgeLabel.mixed,
                "Comparable claims point in opposing directions; this is treated as a true conflict rather than mere heterogeneity.",
                sorted(set(true_conflict_ids)),
            )

        io_groups: dict[tuple[str, str], list[EvidenceClaim]] = {}
        for c in claims:
            io_groups.setdefault((norm(c.intervention_or_exposure), norm(c.outcome)), []).append(c)
        for group in io_groups.values():
            methods = {norm(c.method) for c in group if c.method}
            if len(methods) > 1 and len(group) > 1:
                return JudgeResult(
                    JudgeLabel.methodologically_noncomparable,
                    "Relevant claims use different study methods; apparent disagreement should not be collapsed into a single contradiction label.",
                    [c.claim_id for c in group],
                )

        nonempty_io = {k for k in io_groups if k != ("", "")}
        if len(nonempty_io) > 1:
            return JudgeResult(
                JudgeLabel.heterogeneous,
                "Retrieved claims concern multiple intervention/outcome questions; they should be synthesized by evidence component rather than collapsed into one directional verdict.",
                ids,
            )

        dirs = [c.direction for c in claims if c.direction not in {Direction.descriptive, Direction.mixed}]
        counts = Counter(dirs)
        if not dirs:
            return JudgeResult(JudgeLabel.insufficient, "Claims are descriptive and do not establish a directional evidence pattern.", ids)
        dominant, n = counts.most_common(1)[0]
        if len(claims) >= 3 and n == len(dirs):
            return JudgeResult(JudgeLabel.strongly_consistent, f"All directional claims align ({dominant.value}).", ids)
        if n >= 2 and n == len(dirs):
            return JudgeResult(JudgeLabel.moderately_consistent, f"Available directional claims align ({dominant.value}), but evidence volume is limited.", ids)
        if len(dirs) == 1:
            return JudgeResult(JudgeLabel.insufficient, "Only one directional claim is available.", ids)
        return JudgeResult(JudgeLabel.mixed, "Directional claims are not fully aligned.", ids)
