from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .models import EvidenceClaim, PaperSkill, Provenance


class ExtractionError(ValueError):
    pass


class PaperToSkillFactory:
    """Deterministic MVP ingestion layer.

    Production extraction should use layout-aware parsing, structured extraction
    and human validation. This class intentionally keeps a no-API-key path for
    architecture and regression testing.
    """

    required_metadata = {"paper_id", "citation", "title", "study_type", "population"}

    def from_json(self, path: str | Path) -> PaperSkill:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        skill = PaperSkill.model_validate(data)
        self.validate_semantics(skill)
        return skill

    def from_pdf(self, path: str | Path, metadata: dict[str, Any]) -> PaperSkill:
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        if not text.strip():
            raise ExtractionError("PDF produced no extractable text; use a layout/OCR pipeline in production")
        return self.from_text(text, metadata)

    def from_text(self, text: str, metadata: dict[str, Any]) -> PaperSkill:
        missing = self.required_metadata - metadata.keys()
        if missing:
            raise ExtractionError(f"missing required metadata fields: {sorted(missing)}")
        claims = metadata.get("evidence_claims")
        if not claims:
            claims = [
                EvidenceClaim(
                    claim_id=f"{metadata['paper_id']}-C1",
                    statement=metadata.get("fallback_claim", "No validated scientific claim was supplied."),
                    provenance=[Provenance(source_type="text_span", locator="ingested text", source_span=text[:240])],
                ).model_dump()
            ]
        payload = {
            "paper_id": metadata["paper_id"],
            "citation": metadata["citation"],
            "title": metadata["title"],
            "abstract": metadata.get("abstract", text[:1000]),
            "study_type": metadata["study_type"],
            "population": metadata["population"],
            "setting": metadata.get("setting", []),
            "intervention_or_exposure": metadata.get("intervention_or_exposure", []),
            "comparator": metadata.get("comparator", []),
            "outcomes": metadata.get("outcomes", []),
            "effect_estimates": metadata.get("effect_estimates", []),
            "uncertainty": metadata.get("uncertainty", []),
            "methods": metadata.get("methods", []),
            "evidence_claims": claims,
            "limitations": metadata.get("limitations", []),
            "applicability": metadata.get("applicability", []),
            "safety_boundaries": metadata.get("safety_boundaries", []),
            "resources": metadata.get("resources", []),
            "executable_tools": metadata.get("executable_tools", []),
            "provenance": metadata.get("provenance", [{"source_type": "text_span", "locator": "full text ingestion"}]),
            "related_papers": metadata.get("related_papers", []),
            "metadata": metadata.get("metadata", {}),
        }
        skill = PaperSkill.model_validate(payload)
        self.validate_semantics(skill)
        return skill

    def validate_semantics(self, skill: PaperSkill) -> None:
        for claim in skill.evidence_claims:
            if claim.direction.value in {"beneficial", "harmful"} and not claim.outcome:
                raise ExtractionError(f"directional claim {claim.claim_id} has no outcome")
            if claim.causal_language_allowed and "random" not in skill.study_type.lower() and "trial" not in skill.study_type.lower():
                raise ExtractionError(
                    f"claim {claim.claim_id} permits causal wording but study_type does not look experimental"
                )
