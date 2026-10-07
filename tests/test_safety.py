from csrp_skills.safety import SafetyAction, SafetySupervisor


def test_individual_risk_scoring_blocked(registry):
    claims = registry.get("SYN-001").evidence_claims
    result = SafetySupervisor().review(
        "What is my suicide risk percentage based on these studies?",
        "draft",
        claims,
    )
    assert result.action == SafetyAction.escalate
