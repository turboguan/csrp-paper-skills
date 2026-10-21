from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from .evidence_format import claims_by_id, extract_claim_ids, render_evidence
from .judge import EvidenceJudge
from .llm import LLMMessage
from .organizations.common import OrganizationMessage, OrganizationResult
from .safety import SafetySupervisor


OutputMode = Literal["research", "report", "manuscript", "policy"]


@dataclass(frozen=True)
class CoreAgentRole:
    agent_id: str
    name: str
    function: str
    always_active: bool = False


@dataclass(frozen=True)
class SharedInstitutionalMemory:
    components: tuple[str, ...] = (
        "Paper Skills",
        "Evidence Graph",
        "Provenance Registry",
        "Datasets and analysis artifacts",
        "Prior research outputs",
    )


@dataclass(frozen=True)
class QualitySafetyGate:
    checks: tuple[str, ...] = (
        "evidence sufficiency",
        "claim-level provenance",
        "causal-language discipline",
        "uncertainty and transferability",
        "unsupported-claim detection",
        "individual-risk safety boundary",
        "human-review escalation",
    )
    is_agent: bool = False


@dataclass(frozen=True)
class MinimalVirtualCSRPBlueprint:
    """AI-native Virtual CSRP with the smallest useful separation of functions.

    Four core agent capabilities are available, but only task-relevant agents are
    activated. Shared memory and the quality/safety gate are infrastructure, not
    autonomous agents.
    """

    agents: tuple[CoreAgentRole, ...] = field(default_factory=tuple)
    memory: SharedInstitutionalMemory = field(default_factory=SharedInstitutionalMemory)
    gate: QualitySafetyGate = field(default_factory=QualitySafetyGate)

    @classmethod
    def default(cls) -> "MinimalVirtualCSRPBlueprint":
        return cls(
            agents=(
                CoreAgentRole(
                    "research_coordinator",
                    "Research Coordinator Agent",
                    "Understands the research goal, decomposes the task, activates only needed capabilities, and manages the workflow.",
                    True,
                ),
                CoreAgentRole(
                    "evidence_data",
                    "Evidence & Data Agent",
                    "Retrieves and organizes prior papers, claims, datasets and provenance; identifies what evidence and data are available.",
                    True,
                ),
                CoreAgentRole(
                    "analysis_methods",
                    "Analysis & Methods Agent",
                    "Plans or executes statistical, computational and methodological analysis when the task requires data analysis.",
                    False,
                ),
                CoreAgentRole(
                    "synthesis_decision",
                    "Synthesis & Decision Agent",
                    "Integrates evidence and analysis into a research answer, report, manuscript section or policy memo.",
                    True,
                ),
            )
        )

    @property
    def core_agent_count(self) -> int:
        return len(self.agents)

    def plan(self, query: str, output_mode: OutputMode = "research") -> dict[str, Any]:
        q = query.casefold()
        analysis_terms = (
            "analy", "regression", "model", "dataset", "data ", "estimate",
            "statistic", "causal", "survival", "spatial", "cluster", "predict",
            "forecast", "visual", "plot", "simulation", "robustness",
        )
        needs_analysis = any(term in q for term in analysis_terms)

        active = []
        for agent in self.agents:
            if agent.always_active or agent.agent_id != "analysis_methods" or needs_analysis:
                if agent.agent_id == "analysis_methods" and not needs_analysis:
                    continue
                active.append(agent)

        return {
            "query": query,
            "output_mode": output_mode,
            "active_agents": [asdict(agent) for agent in active],
            "skipped_agents": [
                asdict(agent) for agent in self.agents if agent not in active
            ],
            "shared_memory": list(self.memory.components),
            "quality_safety_gate": {
                "is_agent": self.gate.is_agent,
                "checks": list(self.gate.checks),
            },
        }


class MinimalVirtualCSRPLLMOrganization:
    """Minimal four-capability Virtual CSRP for live LLM research workflows.

    This is a production-style scaffold, not one of the frozen A/B/C experimental
    treatments. It is designed to minimize unnecessary autonomous roles while
    retaining separable evidence, analysis and synthesis functions.
    """

    architecture_name = "minimal_virtual_csrp"

    def __init__(self, blueprint: MinimalVirtualCSRPBlueprint | None = None):
        self.blueprint = blueprint or MinimalVirtualCSRPBlueprint.default()

    @staticmethod
    def _needs_analysis(plan: dict[str, Any]) -> bool:
        return any(
            item["agent_id"] == "analysis_methods"
            for item in plan["active_agents"]
        )

    def run_matched(self, packet, runtime, *, output_mode: OutputMode = "research") -> OrganizationResult:
        skills = list(packet.skills)
        if not skills:
            return OrganizationResult(
                architecture=self.architecture_name,
                query=packet.query,
                answer="No relevant validated claims were retrieved.",
                selected_paper_ids=[],
                provenance={},
                transcript=[
                    OrganizationMessage(
                        actor="QualitySafetyGate",
                        role="evidence_sufficiency",
                        content="No supported evidence was retrieved; the workflow failed closed.",
                    )
                ],
                metrics={
                    **runtime.metrics(),
                    "evidence_count": 0,
                    "claim_count": 0,
                    "persistent_agents": 4,
                    "active_agents": 0,
                    "paper_agents": 0,
                    "shared_evidence_context": True,
                    "coordination_messages": 1,
                    "retriever_id": packet.retriever_id,
                    "evidence_budget": packet.evidence_budget,
                },
                experimental_status="minimal_virtual_csrp_live_scaffold",
            )

        plan = self.blueprint.plan(packet.query, output_mode=output_mode)
        evidence = render_evidence(skills)
        transcript: list[OrganizationMessage] = []

        coordinator = runtime.generate([
            LLMMessage(
                role="system",
                content=(
                    "You are the Research Coordinator of Virtual CSRP. Frame the suicide-prevention "
                    "research question, decompose the work, and specify what evidence or analysis is "
                    "needed. Do not answer the scientific question yet."
                ),
            ),
            LLMMessage(
                role="user",
                content=(
                    f"QUERY:\n{packet.query}\n\n"
                    f"OUTPUT MODE: {output_mode}\n"
                    f"AVAILABLE PAPER IDS: {', '.join(packet.paper_ids)}"
                ),
            ),
        ])
        transcript.append(
            OrganizationMessage(
                actor="ResearchCoordinatorAgent",
                role="coordination",
                content=coordinator.text,
                paper_ids=packet.paper_ids,
                claim_ids=[],
            )
        )

        evidence_response = runtime.generate([
            LLMMessage(
                role="system",
                content=(
                    "You are the Evidence & Data Agent. Retrieve only from the supplied validated "
                    "evidence workspace. Summarize what is supported, what is not supported, key "
                    "study limitations, and data/evidence gaps. Cite claim IDs in square brackets."
                ),
            ),
            LLMMessage(
                role="user",
                content=(
                    f"QUERY:\n{packet.query}\n\n"
                    f"COORDINATOR PLAN:\n{coordinator.text}\n\n"
                    f"VALIDATED EVIDENCE:\n{evidence}"
                ),
            ),
        ])
        evidence_ids = extract_claim_ids(evidence_response.text)
        transcript.append(
            OrganizationMessage(
                actor="EvidenceDataAgent",
                role="evidence_and_data",
                content=evidence_response.text,
                paper_ids=packet.paper_ids,
                claim_ids=evidence_ids,
            )
        )

        methods_text = "No separate analysis step was required for this evidence-synthesis task."
        if self._needs_analysis(plan):
            methods = runtime.generate([
                LLMMessage(
                    role="system",
                    content=(
                        "You are the Analysis & Methods Agent. Using only the supplied evidence, "
                        "identify analyses or methodological reasoning that are justified. If raw "
                        "data are not supplied, do not pretend to have executed a statistical "
                        "analysis. Distinguish completed evidence from proposed analyses."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=(
                        f"QUERY:\n{packet.query}\n\n"
                        f"EVIDENCE AGENT REPORT:\n{evidence_response.text}\n\n"
                        f"VALIDATED EVIDENCE:\n{evidence}"
                    ),
                ),
            ])
            methods_text = methods.text
            transcript.append(
                OrganizationMessage(
                    actor="AnalysisMethodsAgent",
                    role="analysis_and_methods",
                    content=methods.text,
                    paper_ids=packet.paper_ids,
                    claim_ids=extract_claim_ids(methods.text),
                )
            )

        mode_instruction = {
            "research": "Produce a concise research synthesis with implications and evidence gaps.",
            "report": "Produce a structured technical report summary.",
            "manuscript": "Produce a manuscript-ready evidence synthesis paragraph or section with calibrated claims.",
            "policy": "Produce a concise policy evidence memo with supporting evidence, limiting evidence, implementation conditions, uncertainty, transferability, evidence gaps, and a conditional bottom line.",
        }[output_mode]

        synthesis = runtime.generate([
            LLMMessage(
                role="system",
                content=(
                    "You are the Synthesis & Decision Agent. Integrate the coordinator plan, "
                    "evidence report and methods assessment. Preserve uncertainty and study "
                    "differences. Every substantive evidence-based assertion must cite only claim "
                    "IDs that appear in the supplied validated evidence. "
                    + mode_instruction
                ),
            ),
            LLMMessage(
                role="user",
                content=(
                    f"QUERY:\n{packet.query}\n\n"
                    f"COORDINATOR PLAN:\n{coordinator.text}\n\n"
                    f"EVIDENCE & DATA REPORT:\n{evidence_response.text}\n\n"
                    f"ANALYSIS & METHODS REPORT:\n{methods_text}\n\n"
                    f"VALIDATED EVIDENCE:\n{evidence}"
                ),
            ),
        ])
        final_ids = extract_claim_ids(synthesis.text)
        transcript.append(
            OrganizationMessage(
                actor="SynthesisDecisionAgent",
                role="synthesis_and_decision",
                content=synthesis.text,
                paper_ids=packet.paper_ids,
                claim_ids=final_ids,
            )
        )

        claim_map = claims_by_id(skills)
        used_claims = [claim_map[cid] for cid in final_ids if cid in claim_map]
        all_claims = [claim for skill in skills for claim in skill.evidence_claims]
        judge = EvidenceJudge().adjudicate(all_claims)
        safety = SafetySupervisor().review(packet.query, synthesis.text, all_claims)

        gate_message = (
            f"Evidence check: {judge.label.value}. "
            f"Safety action: {safety.action.value}. "
            "Quality & Safety Gate is infrastructure, not an autonomous agent."
        )
        transcript.append(
            OrganizationMessage(
                actor="QualitySafetyGate",
                role="validation_gate",
                content=gate_message,
                paper_ids=packet.paper_ids,
                claim_ids=final_ids,
            )
        )

        metrics = runtime.metrics()
        metrics.update(
            {
                "evidence_count": len(skills),
                "claim_count": len(all_claims),
                "persistent_agents": self.blueprint.core_agent_count,
                "active_agents": len(plan["active_agents"]),
                "paper_agents": 0,
                "shared_evidence_context": True,
                "coordination_messages": len(transcript),
                "retriever_id": packet.retriever_id,
                "evidence_budget": packet.evidence_budget,
                "quality_safety_gate_is_agent": False,
                "output_mode": output_mode,
            }
        )

        return OrganizationResult(
            architecture=self.architecture_name,
            query=packet.query,
            answer=synthesis.text,
            selected_paper_ids=packet.paper_ids,
            provenance={
                claim.claim_id: [p.model_dump() for p in claim.provenance]
                for claim in used_claims
            },
            transcript=transcript,
            metrics=metrics,
            experimental_status="minimal_virtual_csrp_live_scaffold",
        )
