from __future__ import annotations

from .common import OrganizationMessage, OrganizationResult


class SharedKnowledgeOrganization:
    """Paper-as-Skill / umbrella organization.

    Papers remain shared evidence skills rather than persistent paper agents.
    The existing Orchestrator supplies the shared registry/graph reasoning path,
    Evidence Judge and Safety Supervisor.
    """

    architecture_name = "shared_knowledge_umbrella"

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def run(self, query: str) -> OrganizationResult:
        result = self.orchestrator.run(query)
        claim_ids = sorted(result.provenance)
        transcript = [
            OrganizationMessage(
                actor="InstitutionalOrchestrator",
                role="umbrella_coordinator",
                content=(
                    "Retrieves relevant Paper Skills into a shared evidence workspace and delegates "
                    "reasoning to the institutional architecture."
                ),
                paper_ids=result.selected_paper_ids,
                claim_ids=claim_ids,
            ),
            OrganizationMessage(
                actor="EvidenceJudge",
                role="evidence_adjudication",
                content=f"{result.judge.label.value}: {result.judge.rationale}",
                paper_ids=result.selected_paper_ids,
                claim_ids=claim_ids,
            ),
            OrganizationMessage(
                actor="SafetySupervisor",
                role="safety_governance",
                content=f"Safety action: {result.safety.action.value}.",
                paper_ids=result.selected_paper_ids,
                claim_ids=claim_ids,
            ),
        ]

        metrics = result.metrics.to_dict()
        metrics.update(
            {
                "persistent_agents": 1,
                "paper_agents": 0,
                "shared_evidence_context": True,
                "coordination_messages": len(transcript),
                "organizational_form": "shared_knowledge_umbrella",
            }
        )

        return OrganizationResult(
            architecture=self.architecture_name,
            query=query,
            answer=result.answer,
            selected_paper_ids=result.selected_paper_ids,
            provenance=result.provenance,
            transcript=transcript,
            metrics=metrics,
        )
