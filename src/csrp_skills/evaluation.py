from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .baselines import ArchitectureRunner


class BenchmarkQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_id: str
    task_type: str
    query: str
    required_claim_ids: list[str] = Field(default_factory=list)
    notes: str | None = None


class ArchitectureRunRecord(BaseModel):
    query_id: str
    architecture: str
    status: str
    answer: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


def load_queries(path: str | Path) -> list[BenchmarkQuery]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [BenchmarkQuery.model_validate(q) for q in data.get("queries", [])]


def run_query_suite(
    queries: list[BenchmarkQuery],
    runners: list[ArchitectureRunner],
) -> list[ArchitectureRunRecord]:
    """Run available architecture adapters without pretending missing runners exist.

    Unimplemented runners are recorded as not_ready. This makes the experimental
    harness executable before the matched LLM baselines are connected.
    """
    records: list[ArchitectureRunRecord] = []
    for query in queries:
        for runner in runners:
            try:
                out = runner.run(query.query)
            except NotImplementedError as exc:
                records.append(
                    ArchitectureRunRecord(
                        query_id=query.query_id,
                        architecture=runner.name,
                        status="not_ready",
                        error=str(exc),
                    )
                )
                continue
            records.append(
                ArchitectureRunRecord(
                    query_id=query.query_id,
                    architecture=out.architecture,
                    status="completed",
                    answer=out.answer,
                    provenance=out.provenance,
                    metrics=out.metrics,
                )
            )
    return records
