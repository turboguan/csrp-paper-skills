import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from csrp_skills.models import PaperSkill

ROOT = Path(__file__).resolve().parents[1]


def test_sample_skill_validates():
    data = json.loads((ROOT / "sample_skills" / "SYN-001.json").read_text())
    skill = PaperSkill.model_validate(data)
    assert skill.paper_id == "SYN-001"
    assert skill.evidence_claims[0].provenance


def test_claim_without_provenance_fails():
    data = json.loads((ROOT / "sample_skills" / "SYN-001.json").read_text())
    data["evidence_claims"][0]["provenance"] = []
    with pytest.raises(ValidationError):
        PaperSkill.model_validate(data)
