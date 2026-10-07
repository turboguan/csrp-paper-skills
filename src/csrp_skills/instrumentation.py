from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class RunMetrics:
    architecture: str
    latency_ms: float
    evidence_count: int
    claim_count: int
    coordination_messages: int
    llm_calls: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None

    def to_dict(self):
        return asdict(self)
