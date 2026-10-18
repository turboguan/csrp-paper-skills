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


    def run_matched(self, packet, runtime) -> OrganizationResult:
        """Run one isolated LLM PaperAgent per paper, then a chair synthesis."""
        from ..evidence_format import claims_by_id, extract_claim_ids, render_paper_skill
        from ..llm import LLMMessage

        skills = list(packet.skills)
        if not skills:
            return self.no_evidence_result(packet.query)

        transcript = [
            OrganizationMessage(
                actor="CommitteeChair",
                role="chair",
                content=f"Convenes {len(skills)} PaperAgents using the identical matched EvidencePacket.",
                paper_ids=packet.paper_ids,
            )
        ]
        reports = []
        for skill in skills:
            evidence = render_paper_skill(skill)
            response = runtime.generate([
                LLMMessage(role="system", content="You are a PaperAgent. You may use only the single paper supplied to you. State what this paper supports, does not support, and its limitations. Cite claim IDs in square brackets."),
                LLMMessage(role="user", content=f"QUERY:\n{packet.query}\n\nYOUR PAPER ONLY:\n{evidence}"),
            ])
            reports.append((skill.paper_id, response.text))
            transcript.append(
                OrganizationMessage(
                    actor=f"PaperAgent[{skill.paper_id}]",
                    role="paper_expert",
                    content=response.text,
                    paper_ids=[skill.paper_id],
                    claim_ids=extract_claim_ids(response.text),
                )
            )

        report_text = "\n\n".join(f"{paper_id}:\n{text}" for paper_id, text in reports)
        chair = runtime.generate([
            LLMMessage(role="system", content="You are the CommitteeChair. Integrate isolated PaperAgent reports into one answer. Preserve disagreements and limitations; do not create evidence absent from the reports. Cite claim IDs in square brackets."),
            LLMMessage(role="user", content=f"QUERY:\n{packet.query}\n\nPAPER-AGENT REPORTS:\n{report_text}"),
        ])
        final_ids = extract_claim_ids(chair.text)
        claim_map = claims_by_id(skills)
        used_claims = [claim_map[cid] for cid in final_ids if cid in claim_map]
        transcript.append(
            OrganizationMessage(
                actor="CommitteeChair",
                role="chair",
                content=chair.text,
                paper_ids=packet.paper_ids,
                claim_ids=final_ids,
            )
        )

        metrics = runtime.metrics()
        metrics.update({
            "evidence_count": len(skills),
            "claim_count": sum(len(skill.evidence_claims) for skill in skills),
            "persistent_agents": 1,
            "paper_agents": len(skills),
            "shared_evidence_context": False,
            "coordination_messages": len(transcript),
            "retriever_id": packet.retriever_id,
            "evidence_budget": packet.evidence_budget,
        })
        return OrganizationResult(
            architecture=self.architecture_name,
            query=packet.query,
            answer=chair.text,
            selected_paper_ids=packet.paper_ids,
            provenance=self.provenance_for_claims(used_claims),
            transcript=transcript,
            metrics=metrics,
            experimental_status="matched_llm_scaffold",
        )
