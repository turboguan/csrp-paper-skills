from csrp_skills.judge import EvidenceJudge, JudgeLabel


def test_judge_true_conflict(registry):
    claims = registry.get("SYN-004").evidence_claims + registry.get("SYN-005").evidence_claims
    result = EvidenceJudge().adjudicate(claims)
    assert result.label == JudgeLabel.mixed


def test_judge_population_mismatch(registry):
    claims = registry.get("SYN-001").evidence_claims + registry.get("SYN-003").evidence_claims
    result = EvidenceJudge().adjudicate(claims, target_population="older adults")
    assert result.label == JudgeLabel.population_mismatch
