from pathlib import Path

import pytest

from csrp_skills.factory import PaperToSkillFactory
from csrp_skills.graph import EvidenceGraph
from csrp_skills.orchestrator import Orchestrator
from csrp_skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def registry():
    factory = PaperToSkillFactory()
    r = SkillRegistry()
    for path in sorted((ROOT / "sample_skills").glob("*.json")):
        r.register(factory.from_json(path))
    return r


@pytest.fixture
def graph(registry):
    return EvidenceGraph().build_graph(registry.all())


@pytest.fixture
def system(registry, graph):
    return Orchestrator(registry, graph)
