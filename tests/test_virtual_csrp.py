from csrp_skills.virtual_csrp import VirtualCSRPBlueprint, VirtualCSRPInstitute


class DummyArchitecture:
    def __init__(self, name):
        self.name = name

    def run(self, query):
        return {"architecture": self.name, "query": query}


def test_default_blueprint_contains_five_units_and_four_services():
    blueprint = VirtualCSRPBlueprint.default()
    assert len(blueprint.units) == 5
    assert len(blueprint.services) == 4
    assert set(blueprint.governance_roles) == {"Evidence Judge", "Safety Supervisor"}


def test_policy_query_routes_to_policy_unit():
    blueprint = VirtualCSRPBlueprint.default()
    units = blueprint.route_units("What policy and implementation strategy should be considered?")
    assert units[0].unit_id == "policy_implementation"


def test_unknown_query_fails_to_methods_and_evidence_unit():
    blueprint = VirtualCSRPBlueprint.default()
    units = blueprint.route_units("Completely unrelated vocabulary")
    assert [unit.unit_id for unit in units] == ["methods_evidence"]


def test_virtual_institute_wraps_all_three_organizational_designs():
    institute = VirtualCSRPInstitute(
        {
            "functional_multi_agent": DummyArchitecture("A"),
            "paper_agent_committee": DummyArchitecture("B"),
            "shared_knowledge_umbrella": DummyArchitecture("C"),
        }
    )
    assert institute.available_architectures() == [
        "functional_multi_agent",
        "paper_agent_committee",
        "shared_knowledge_umbrella",
    ]
    assert institute.run("test query", "paper_agent_committee")["architecture"] == "B"


def test_community_service_retains_safety_boundary():
    blueprint = VirtualCSRPBlueprint.default()
    community = next(service for service in blueprint.services if service.service_id == "community")
    assert community.safety_boundary is not None
    assert "risk scoring" in community.safety_boundary
