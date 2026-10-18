from __future__ import annotations

from collections import Counter

from .common import BaseEvidenceOrganization, OrganizationMessage, OrganizationResult


class FunctionalMultiAgentOrganization(BaseEvidenceOrganization):
    """Shared-corpus, task-specialized agent organization.

    All specialist roles can access the same retrieved evidence workspace.
    The current implementation is deterministic and exposes the organizational
    structure only; LLM reasoning will be added later under matched model budgets.
    """

    architecture_name = "functional_multi_agent"

    roles = (
        "PerspectiveAgent",
        "PredictAgent",
        "StrategyAgent",
        "ExternalAgent",
        "DecisionAgent",
    )

    def _perspective(self, workspace) -> str:
        populations = sorted({c.population for c in workspace.claims if c.population})
        methods = sorted({c.method for c in workspace.claims if c.method})
        return (
            "Maps heterogeneity across populations and study perspectives. "
            f"Populations represented: {populations or ['not specified']}. "
            f"Methods represented: {methods or ['not specified']}."
        )

    def _predict(self, workspace) -> str:
        directions = Counter(c.direction.value for c in workspace.claims)
        return (
            "Summarizes observed evidence directions without extrapolating a future outcome. "
            f"Observed claim directions: {dict(directions)}."
        )

    def _strategy(self, workspace) -> str:
        applicability = [item for skill in workspace.skills for item in skill.applicability]
        limitations = [item for skill in workspace.skills for item in skill.limitations]
        return (
            "Surfaces evidence relevant to strategy formation while preserving limitations. "
            f"Applicability notes: {applicability[:4]}. Limitations: {limitations[:4]}."
        )

    def _external(self, workspace) -> str:
        settings = sorted({setting for skill in workspace.skills for setting in skill.setting})
        return (
            "Reviews external context and transferability across settings. "
            f"Settings represented: {settings or ['not specified']}."
        )

    def _decision(self, workspace) -> str:
        lines = ["Integrates specialist inputs using the shared evidence workspace:"]
        for claim in workspace.claims:
            lines.append(f"- [{claim.claim_id}] {claim.statement}")
        return "\n".join(lines)

    def run(self, query: str) -> OrganizationResult:
        skills = self.retrieve(query)
        if not skills:
            return self.no_evidence_result(query)

        workspace = self.workspace(query, skills)
        claims = workspace.claims
        if not claims:
            return self.no_evidence_result(query)

        transcript = [
            OrganizationMessage(
                actor="FacilitatorAgent",
                role="facilitator",
                content=(
                    "Dispatches the same retrieved evidence workspace to five task-specialized roles "
                    "and coordinates their outputs."
                ),
                paper_ids=[s.paper_id for s in skills],
                claim_ids=[c.claim_id for c in claims],
            )
        ]

        handlers = {
            "PerspectiveAgent": self._perspective,
            "PredictAgent": self._predict,
            "StrategyAgent": self._strategy,
            "ExternalAgent": self._external,
            "DecisionAgent": self._decision,
        }

        for role in self.roles:
            transcript.append(
                OrganizationMessage(
                    actor=role,
                    role=role.removesuffix("Agent").casefold(),
                    content=handlers[role](workspace),
                    paper_ids=[s.paper_id for s in skills],
                    claim_ids=[c.claim_id for c in claims],
                )
            )

        final = transcript[-1].content
        transcript.append(
            OrganizationMessage(
                actor="FacilitatorAgent",
                role="facilitator",
                content="Closes the cycle and returns the DecisionAgent synthesis as the organizational output.",
                paper_ids=[s.paper_id for s in skills],
                claim_ids=[c.claim_id for c in claims],
            )
        )

        return OrganizationResult(
            architecture=self.architecture_name,
            query=query,
            answer=final,
            selected_paper_ids=[s.paper_id for s in skills],
            provenance=self.provenance_for_claims(claims),
            transcript=transcript,
            metrics={
                "evidence_count": len(skills),
                "claim_count": len(claims),
                "persistent_agents": 6,
                "paper_agents": 0,
                "shared_evidence_context": True,
                "coordination_messages": len(transcript),
                "llm_calls": 0,
            },
        )


    def run_matched(self, packet, runtime) -> OrganizationResult:
        """Run the functional organization on a pre-retrieved matched evidence packet."""
        from ..evidence_format import claims_by_id, extract_claim_ids, render_evidence
        from ..llm import LLMMessage

        skills = list(packet.skills)
        if not skills:
            return self.no_evidence_result(packet.query)

        evidence = render_evidence(skills)
        transcript = [
            OrganizationMessage(
                actor="FacilitatorAgent",
                role="facilitator",
                content="Dispatches the identical matched EvidencePacket to four specialist roles.",
                paper_ids=packet.paper_ids,
            )
        ]

        role_prompts = {
            "PerspectiveAgent": "Identify distinct populations, study perspectives, methods and important heterogeneity. Do not invent evidence.",
            "PredictAgent": "Assess what the observed evidence can and cannot support about expected outcomes. Do not extrapolate beyond the supplied evidence.",
            "StrategyAgent": "Identify strategy-relevant implications, limitations and applicability conditions from the supplied evidence.",
            "ExternalAgent": "Assess external context, setting differences and transferability limits in the supplied evidence.",
        }
        specialist_outputs = []
        for role, instruction in role_prompts.items():
            response = runtime.generate([
                LLMMessage(role="system", content="You are a task-specialized member of an evidence-review organization. Cite claim IDs in square brackets for every evidence-based assertion."),
                LLMMessage(role="user", content=f"QUERY:\n{packet.query}\n\nROLE:\n{instruction}\n\nEVIDENCE:\n{evidence}"),
            ])
            specialist_outputs.append((role, response.text))
            transcript.append(
                OrganizationMessage(
                    actor=role,
                    role=role.removesuffix("Agent").casefold(),
                    content=response.text,
                    paper_ids=packet.paper_ids,
                    claim_ids=extract_claim_ids(response.text),
                )
            )

        specialist_text = "\n\n".join(f"{role}:\n{text}" for role, text in specialist_outputs)
        final = runtime.generate([
            LLMMessage(role="system", content="You are the DecisionAgent. Integrate the specialist reports into one evidence-grounded answer. Resolve disagreement explicitly. Cite only claim IDs present in the supplied evidence."),
            LLMMessage(role="user", content=f"QUERY:\n{packet.query}\n\nEVIDENCE:\n{evidence}\n\nSPECIALIST REPORTS:\n{specialist_text}"),
        ])
        final_ids = extract_claim_ids(final.text)
        claim_map = claims_by_id(skills)
        used_claims = [claim_map[cid] for cid in final_ids if cid in claim_map]
        transcript.append(
            OrganizationMessage(
                actor="DecisionAgent",
                role="decision",
                content=final.text,
                paper_ids=packet.paper_ids,
                claim_ids=final_ids,
            )
        )

        metrics = runtime.metrics()
        metrics.update({
            "evidence_count": len(skills),
            "claim_count": sum(len(skill.evidence_claims) for skill in skills),
            "persistent_agents": 6,
            "paper_agents": 0,
            "shared_evidence_context": True,
            "coordination_messages": len(transcript),
            "retriever_id": packet.retriever_id,
            "evidence_budget": packet.evidence_budget,
        })
        return OrganizationResult(
            architecture=self.architecture_name,
            query=packet.query,
            answer=final.text,
            selected_paper_ids=packet.paper_ids,
            provenance=self.provenance_for_claims(used_claims),
            transcript=transcript,
            metrics=metrics,
            experimental_status="matched_llm_scaffold",
        )
