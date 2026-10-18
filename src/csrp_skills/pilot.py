from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PilotQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_id: str
    complexity: Literal["low", "medium", "high", "adversarial"]
    task_interdependence: int
    task_uncertainty: int
    task_type: str
    query: str
    expected_mode: Literal["evidence", "no_evidence"]
    required_paper_ids: list[str] = Field(default_factory=list)
    required_claim_ids: list[str] = Field(default_factory=list)
    human_review_required: bool = False


class MeansPilotSuite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pilot_id: str
    status: str
    corpus_paper_ids: list[str]
    purpose: str
    replicates_per_architecture_query: int
    scientific_boundary: str
    questions: list[PilotQuestion]


def load_means_pilot(path: str | Path) -> MeansPilotSuite:
    return MeansPilotSuite.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
