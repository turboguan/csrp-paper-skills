from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Direction(str, Enum):
    beneficial = "beneficial"
    harmful = "harmful"
    null = "null"
    mixed = "mixed"
    descriptive = "descriptive"


class Provenance(BaseModel):
    source_type: Literal["page", "table", "figure", "supplement", "text_span", "metadata"]
    locator: str
    source_span: str | None = None


class EffectEstimate(BaseModel):
    outcome: str
    measure: str | None = None
    estimate: float | str | None = None
    lower_ci: float | None = None
    upper_ci: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def ci_is_ordered(self):
        if self.lower_ci is not None and self.upper_ci is not None and self.lower_ci > self.upper_ci:
            raise ValueError("lower_ci must be <= upper_ci")
        return self


class EvidenceClaim(BaseModel):
    claim_id: str
    statement: str
    direction: Direction = Direction.descriptive
    population: str | None = None
    intervention_or_exposure: str | None = None
    outcome: str | None = None
    method: str | None = None
    causal_language_allowed: bool = False
    provenance: list[Provenance] = Field(default_factory=list)

    @field_validator("provenance")
    @classmethod
    def claim_requires_provenance(cls, value: list[Provenance]):
        if not value:
            raise ValueError("every claim must include at least one provenance anchor")
        return value


class Resource(BaseModel):
    kind: Literal["paper", "supplement", "dataset", "code", "table", "figure", "other"]
    uri: str
    description: str | None = None


class ExecutableTool(BaseModel):
    name: str
    description: str
    entrypoint: str | None = None
    validated: bool = False


class PaperSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper_id: str
    citation: str
    title: str
    abstract: str = ""
    study_type: str
    population: list[str]
    setting: list[str] = Field(default_factory=list)
    intervention_or_exposure: list[str] = Field(default_factory=list)
    comparator: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    effect_estimates: list[EffectEstimate] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    evidence_claims: list[EvidenceClaim]
    limitations: list[str] = Field(default_factory=list)
    applicability: list[str] = Field(default_factory=list)
    safety_boundaries: list[str] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)
    executable_tools: list[ExecutableTool] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    related_papers: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_claim_ids(self):
        ids = [c.claim_id for c in self.evidence_claims]
        if len(ids) != len(set(ids)):
            raise ValueError("claim_id values must be unique within a paper skill")
        for claim in self.evidence_claims:
            if claim.population and self.population and claim.population not in self.population:
                raise ValueError(f"claim population {claim.population!r} is absent from paper population")
            if claim.outcome and self.outcomes and claim.outcome not in self.outcomes:
                raise ValueError(f"claim outcome {claim.outcome!r} is absent from paper outcomes")
        return self

    def claim_ids(self) -> list[str]:
        return [c.claim_id for c in self.evidence_claims]
