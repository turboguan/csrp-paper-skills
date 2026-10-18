from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .llm import LLMAdapter
from .retrieval import EvidencePacket, FixedEvidenceRetriever
from .runtime import LLMRuntime, MatchedBudget


@dataclass
class MatchedArchitectureRecord:
    query: str
    architecture: str
    answer: str
    selected_paper_ids: list[str]
    provenance: dict
    transcript: list[dict]
    metrics: dict
    experimental_status: str


@dataclass
class MatchedQueryResult:
    query: str
    evidence_packet: dict
    records: list[MatchedArchitectureRecord]


class MatchedExperimentRunner:
    """Runs multiple organizational forms on one identical evidence packet.

    The retriever executes once per query. Each organization receives:
    - the exact same EvidencePacket;
    - the exact same LLMAdapter instance/model;
    - an independent tracker initialized from the exact same MatchedBudget.
    """

    def __init__(
        self,
        *,
        retriever: FixedEvidenceRetriever,
        adapter: LLMAdapter,
        budget: MatchedBudget,
        organizations: Iterable,
    ):
        self.retriever = retriever
        self.adapter = adapter
        self.budget = budget
        self.organizations = list(organizations)

    def run_query(self, query: str) -> MatchedQueryResult:
        packet = self.retriever.retrieve(query)
        records: list[MatchedArchitectureRecord] = []

        for organization in self.organizations:
            runtime = LLMRuntime(self.adapter, self.budget)
            result = organization.run_matched(packet, runtime)
            if result.selected_paper_ids != packet.paper_ids:
                raise AssertionError(
                    f"architecture {result.architecture} changed the matched evidence packet"
                )
            if result.metrics.get("evidence_budget") != packet.evidence_budget:
                raise AssertionError("architecture changed the evidence budget")
            model_id = result.metrics.get("model_id")
            if packet.paper_ids and model_id != self.adapter.model_id:
                raise AssertionError("architecture did not use the matched LLM adapter/model")
            if result.metrics.get("total_tokens", 0) > self.budget.max_total_tokens:
                raise AssertionError("architecture exceeded the matched total-token budget")

            records.append(
                MatchedArchitectureRecord(
                    query=query,
                    architecture=result.architecture,
                    answer=result.answer,
                    selected_paper_ids=result.selected_paper_ids,
                    provenance=result.provenance,
                    transcript=[asdict(message) for message in result.transcript],
                    metrics=result.metrics,
                    experimental_status=result.experimental_status,
                )
            )

        return MatchedQueryResult(
            query=query,
            evidence_packet={
                "retriever_id": packet.retriever_id,
                "evidence_budget": packet.evidence_budget,
                "paper_ids": packet.paper_ids,
            },
            records=records,
        )
