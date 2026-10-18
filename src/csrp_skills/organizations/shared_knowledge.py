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


    def run_matched(self, packet, runtime) -> OrganizationResult:
        """Run one institutional reasoning context over the matched shared evidence packet."""
        from ..evidence_format import claims_by_id, extract_claim_ids, render_evidence
        from ..llm import LLMMessage
        from ..judge import EvidenceJudge
        from ..safety import SafetySupervisor

        skills = list(packet.skills)
        if not skills:
            return OrganizationResult(
                architecture=self.architecture_name,
                query=packet.query,
                answer="No relevant validated claims were retrieved.",
                selected_paper_ids=[],
                provenance={},
                transcript=[OrganizationMessage(actor="EvidenceGate", role="evidence_sufficiency", content="No supported evidence was retrieved; the organization failed closed.")],
                metrics={**runtime.metrics(), "evidence_count": 0, "claim_count": 0, "retriever_id": packet.retriever_id, "evidence_budget": packet.evidence_budget},
                experimental_status="matched_llm_scaffold",
            )

        evidence = render_evidence(skills)
        response = runtime.generate([
            LLMMessage(role="system", content="You are an institutional co-scientist reasoning over a shared multi-paper evidence workspace. Compare evidence directly, preserve uncertainty and study differences, and cite claim IDs in square brackets."),
            LLMMessage(role="user", content=f"QUERY:\n{packet.query}\n\nSHARED EVIDENCE WORKSPACE:\n{evidence}"),
        ])
        final_ids = extract_claim_ids(response.text)
        claim_map = claims_by_id(skills)
        used_claims = [claim_map[cid] for cid in final_ids if cid in claim_map]
        all_claims = [claim for skill in skills for claim in skill.evidence_claims]
        judge = EvidenceJudge().adjudicate(all_claims)
        safety = SafetySupervisor().review(packet.query, response.text, all_claims)
        transcript = [
            OrganizationMessage(actor="InstitutionalOrchestrator", role="umbrella_coordinator", content=response.text, paper_ids=packet.paper_ids, claim_ids=final_ids),
            OrganizationMessage(actor="EvidenceJudge", role="evidence_adjudication", content=f"{judge.label.value}: {judge.rationale}", paper_ids=packet.paper_ids, claim_ids=final_ids),
            OrganizationMessage(actor="SafetySupervisor", role="safety_governance", content=f"Safety action: {safety.action.value}.", paper_ids=packet.paper_ids, claim_ids=final_ids),
        ]

        metrics = runtime.metrics()
        metrics.update({
            "evidence_count": len(skills),
            "claim_count": len(all_claims),
            "persistent_agents": 1,
            "paper_agents": 0,
            "shared_evidence_context": True,
            "coordination_messages": len(transcript),
            "retriever_id": packet.retriever_id,
            "evidence_budget": packet.evidence_budget,
        })
        return OrganizationResult(
            architecture=self.architecture_name,
            query=packet.query,
            answer=response.text,
            selected_paper_ids=packet.paper_ids,
            provenance={claim.claim_id: [p.model_dump() for p in claim.provenance] for claim in used_claims},
            transcript=transcript,
            metrics=metrics,
            experimental_status="matched_llm_scaffold",
        )
