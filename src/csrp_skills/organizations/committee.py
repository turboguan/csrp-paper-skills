from __future__ import annotations

from .common import BaseEvidenceOrganization, OrganizationMessage, OrganizationResult


class PaperAgentCommittee(BaseEvidenceOrganization):
    """One paper = one isolated agent, followed by a coordinating chair.

    Each PaperAgent sees only its own Paper Skill. The CommitteeChair receives
    the paper-agent statements and integrates them. The deterministic scaffold
    makes context isolation explicit so it can later be compared fairly with
    shared-context architectures.
    """

    architecture_name = "paper_agent_committee"

    def run(self, query: str) -> OrganizationResult:
        skills = self.retrieve(query)
        if not skills:
            return self.no_evidence_result(query)

        transcript: list[OrganizationMessage] = [
            OrganizationMessage(
                actor="CommitteeChair",
                role="chair",
                content=f"Convenes {len(skills)} isolated PaperAgent(s) for the same query.",
                paper_ids=[s.paper_id for s in skills],
            )
        ]

        all_claims = []
        paper_statements: list[str] = []

        for skill in skills:
            private_workspace = self.workspace(query, [skill])
            claims = private_workspace.claims
            all_claims.extend(claims)
            if claims:
                statement = "\n".join(
                    [f"- [{claim.claim_id}] {claim.statement}" for claim in claims]
                )
            else:
                statement = "No query-relevant claim was selected from this paper."
            paper_statements.append(f"{skill.paper_id}:\n{statement}")
            transcript.append(
                OrganizationMessage(
                    actor=f"PaperAgent[{skill.paper_id}]",
                    role="paper_expert",
                    content=statement,
                    paper_ids=[skill.paper_id],
                    claim_ids=[c.claim_id for c in claims],
                )
            )

        answer = (
            "CommitteeChair synthesis from isolated paper-agent reports:\n"
            + "\n".join(paper_statements)
        )

        transcript.append(
            OrganizationMessage(
                actor="CommitteeChair",
                role="chair",
                content=(
                    "Aggregates the isolated paper-agent reports. "
                    "No shared paper-level reasoning context is assumed in this scaffold."
                ),
                paper_ids=[s.paper_id for s in skills],
                claim_ids=[c.claim_id for c in all_claims],
            )
        )

        return OrganizationResult(
            architecture=self.architecture_name,
            query=query,
            answer=answer,
            selected_paper_ids=[s.paper_id for s in skills],
            provenance=self.provenance_for_claims(all_claims),
            transcript=transcript,
            metrics={
                "evidence_count": len(skills),
                "claim_count": len(all_claims),
                "persistent_agents": 1,
                "paper_agents": len(skills),
                "shared_evidence_context": False,
                "coordination_messages": len(transcript),
                "llm_calls": 0,
            },
        )
