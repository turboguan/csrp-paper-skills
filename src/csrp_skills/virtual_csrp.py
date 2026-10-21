from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class InstitutionalUnit:
    unit_id: str
    name: str
    mission: str
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class ServiceChannel:
    service_id: str
    name: str
    purpose: str
    safety_boundary: str | None = None


@dataclass(frozen=True)
class VirtualCSRPBlueprint:
    """Institution-level scaffold above the existing evidence and organization layers.

    This object describes the Virtual CSRP as an AI research institute. It does not
    make scientific claims and does not replace the matched A/B/C experiment.
    """

    director: str = "Director / PI Agent"
    coordinator: str = "Chief of Staff / Query Router"
    units: tuple[InstitutionalUnit, ...] = field(default_factory=tuple)
    services: tuple[ServiceChannel, ...] = field(default_factory=tuple)
    governance_roles: tuple[str, ...] = ("Evidence Judge", "Safety Supervisor")

    @classmethod
    def default(cls) -> "VirtualCSRPBlueprint":
        return cls(
            units=(
                InstitutionalUnit(
                    "surveillance_epidemiology",
                    "Surveillance & Epidemiology Unit",
                    "Trends, risk factors, population patterns and surveillance evidence.",
                    ("trend", "surveillance", "epidemiology", "risk factor", "population", "cluster"),
                ),
                InstitutionalUnit(
                    "intervention_evaluation",
                    "Intervention & Evaluation Unit",
                    "Intervention evidence, programme evaluation and implementation science.",
                    ("intervention", "programme", "program", "evaluation", "effect", "trial", "implementation"),
                ),
                InstitutionalUnit(
                    "policy_implementation",
                    "Policy & Implementation Unit",
                    "Policy analysis, evidence-to-action translation and resource-allocation reasoning.",
                    ("policy", "guideline", "strategy", "resource", "regulation", "implementation"),
                ),
                InstitutionalUnit(
                    "practitioner_community",
                    "Practitioner & Community Support Unit",
                    "Practice-facing evidence, community resources and human-centred implementation.",
                    ("practitioner", "community", "school", "social worker", "practice", "service"),
                ),
                InstitutionalUnit(
                    "methods_evidence",
                    "Methods & Evidence Unit",
                    "Study design, synthesis, causal inference, provenance and methodological quality.",
                    ("method", "bias", "causal", "provenance", "evidence", "synthesis", "design"),
                ),
            ),
            services=(
                ServiceChannel("research", "Research Co-Scientist", "Evidence synthesis, gap discovery, hypothesis and study-design support."),
                ServiceChannel("policy", "Policy Intelligence", "Evidence-grounded policy synthesis and decision support."),
                ServiceChannel("practice", "Practitioner Guidance", "Evidence summaries and implementation support for practitioners."),
                ServiceChannel(
                    "community",
                    "Community / Individual Support",
                    "Accessible evidence-grounded information and signposting.",
                    "No autonomous individual suicide-risk scoring, diagnosis, triage or treatment selection.",
                ),
            ),
        )

    def route_units(self, query: str, *, max_units: int = 3) -> list[InstitutionalUnit]:
        """Deterministic routing scaffold for architecture demos.

        It is intentionally simple and auditable. Later work can replace it with a
        matched learned router, but only under a frozen experimental protocol.
        """
        q = query.casefold()
        scored: list[tuple[int, InstitutionalUnit]] = []
        for unit in self.units:
            score = sum(1 for keyword in unit.keywords if keyword in q)
            scored.append((score, unit))
        scored.sort(key=lambda item: (-item[0], item[1].unit_id))
        selected = [unit for score, unit in scored if score > 0][:max_units]
        if selected:
            return selected
        # Fail to a methodological/evidence unit rather than inventing a domain.
        return [next(unit for unit in self.units if unit.unit_id == "methods_evidence")]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VirtualCSRPInstitute:
    """Thin institutional wrapper around the three existing organization designs.

    The same evidence substrate and matched-runner controls remain downstream.
    Virtual CSRP adds an institute-level identity, routing vocabulary and service
    map without silently changing the A/B/C comparison.
    """

    def __init__(self, architectures: Mapping[str, Any], blueprint: VirtualCSRPBlueprint | None = None):
        self.blueprint = blueprint or VirtualCSRPBlueprint.default()
        self.architectures = dict(architectures)

    def available_architectures(self) -> list[str]:
        return sorted(self.architectures)

    def plan(self, query: str) -> dict[str, Any]:
        units = self.blueprint.route_units(query)
        return {
            "query": query,
            "director": self.blueprint.director,
            "coordinator": self.blueprint.coordinator,
            "routed_units": [asdict(unit) for unit in units],
            "governance_roles": list(self.blueprint.governance_roles),
        }

    def run(self, query: str, architecture_id: str):
        if architecture_id not in self.architectures:
            raise KeyError(
                f"Unknown architecture {architecture_id!r}. "
                f"Available: {', '.join(self.available_architectures())}"
            )
        return self.architectures[architecture_id].run(query)
