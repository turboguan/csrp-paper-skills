from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkOutput:
    architecture: str
    answer: str
    provenance: dict[str, Any]
    metrics: dict[str, Any]


class ArchitectureRunner(ABC):
    name: str

    @abstractmethod
    def run(self, query: str) -> BenchmarkOutput:
        raise NotImplementedError


class RAGOnlyRunner(ArchitectureRunner):
    name = "rag_only"
    def run(self, query: str) -> BenchmarkOutput:
        raise NotImplementedError("Connect a matched retriever + LLM before benchmarking")


class MonolithicAgentRunner(ArchitectureRunner):
    name = "monolithic_agent"
    def run(self, query: str) -> BenchmarkOutput:
        raise NotImplementedError("Connect the same base LLM and corpus before benchmarking")


class OnePaperOneAgentRunner(ArchitectureRunner):
    name = "one_paper_one_agent"
    def run(self, query: str) -> BenchmarkOutput:
        raise NotImplementedError("Implement one isolated reasoning unit per retrieved paper and an aggregator")


class PaperAsSkillRunner(ArchitectureRunner):
    name = "paper_as_skill"

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def run(self, query: str) -> BenchmarkOutput:
        result = self.orchestrator.run(query)
        return BenchmarkOutput(
            architecture=self.name,
            answer=result.answer,
            provenance=result.provenance,
            metrics=result.metrics.to_dict(),
        )
