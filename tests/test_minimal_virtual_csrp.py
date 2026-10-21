from csrp_skills.minimal_virtual_csrp import MinimalVirtualCSRPBlueprint


def test_minimal_virtual_csrp_has_four_core_agents():
    bp = MinimalVirtualCSRPBlueprint.default()
    assert bp.core_agent_count == 4
    assert [a.agent_id for a in bp.agents] == [
        "research_coordinator",
        "evidence_data",
        "analysis_methods",
        "synthesis_decision",
    ]


def test_literature_task_uses_three_active_agents():
    bp = MinimalVirtualCSRPBlueprint.default()
    plan = bp.plan(
        "Summarize what the charcoal-restriction papers conclude and their limitations.",
        output_mode="research",
    )
    ids = [item["agent_id"] for item in plan["active_agents"]]
    assert ids == [
        "research_coordinator",
        "evidence_data",
        "synthesis_decision",
    ]


def test_analysis_task_activates_methods_agent():
    bp = MinimalVirtualCSRPBlueprint.default()
    plan = bp.plan(
        "Analyze the dataset using spatial regression and produce a report.",
        output_mode="report",
    )
    ids = [item["agent_id"] for item in plan["active_agents"]]
    assert "analysis_methods" in ids
    assert len(ids) == 4


def test_quality_and_safety_is_gate_not_agent():
    bp = MinimalVirtualCSRPBlueprint.default()
    plan = bp.plan("Summarize prior evidence.")
    assert plan["quality_safety_gate"]["is_agent"] is False
    assert "individual-risk safety boundary" in plan["quality_safety_gate"]["checks"]


def test_shared_memory_is_infrastructure():
    bp = MinimalVirtualCSRPBlueprint.default()
    plan = bp.plan("Summarize prior evidence.")
    assert "Paper Skills" in plan["shared_memory"]
    assert "Evidence Graph" in plan["shared_memory"]
