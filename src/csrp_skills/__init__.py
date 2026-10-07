"""CSRP Paper-as-Skill research prototype."""

from .models import PaperSkill, EvidenceClaim, Provenance
from .registry import SkillRegistry
from .graph import EvidenceGraph
from .judge import EvidenceJudge
from .safety import SafetySupervisor
from .orchestrator import Orchestrator
from .benchmark import RelationLabel, ClaimPairGold, RelationPrediction, score_relations

__all__ = [
    "PaperSkill", "EvidenceClaim", "Provenance", "SkillRegistry", "EvidenceGraph",
    "EvidenceJudge", "SafetySupervisor", "Orchestrator", "RelationLabel",
    "ClaimPairGold", "RelationPrediction", "score_relations",
]
