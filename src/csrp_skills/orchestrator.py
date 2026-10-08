from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass

from .agents import DomainAgent, EvidenceWorkspace
from .graph import EvidenceGraph
from .instrumentation import RunMetrics
from .judge import EvidenceJudge, JudgeResult
from .models import PaperSkill
from .registry import SkillRegistry
from .router import QueryRouter, Route
from .safety import SafetyAction, SafetyResult, SafetySupervisor


@dataclass
class OrchestratorResult:
    query: str
    route: Route
    selected_paper_ids: list[str]
    judge: JudgeResult
    safety: SafetyResult
    answer: str
    provenance: dict[str, list[dict]]
    metrics: RunMetrics

    def to_dict(self):
        data = asdict(self)
        data["judge"]["label"] = self.judge.label.value
        data["safety"]["action"] = self.safety.action.value
        return data


class Orchestrator:
    def __init__(self, registry: SkillRegistry, graph: EvidenceGraph):
        self.registry = registry
        self.graph = graph
        self.router = QueryRouter()
        self.judge = EvidenceJudge()
        self.safety = SafetySupervisor()
        self.agents = {role: DomainAgent(role) for role in ("Universal", "Selective", "Indicated")}

    def _target_population(self, query: str) -> str | None:
        q = query.casefold()
        for term in ["older adults", "elderly", "adolescents", "adolescent", "youth", "veterans", "veteran"]:
            if term in q:
                return term
        return None

    def _retrieve(self, query: str) -> list[PaperSkill]:
        match = re.search(r"(?:SYN-\d{3}|CSRP-REAL-\d{3}|V03-[A-Z]+-\d{3})", query.upper())
        if match:
            try:
                return [self.registry.get(match.group(0))]
            except KeyError:
                return []
        hits = self.registry.keyword_search(query, limit=12)
        if hits:
            return hits
        # Fail closed: an unsupported or irrelevant query must not receive
        # arbitrary corpus evidence. The previous fallback to the first five
        # registered skills could make the system appear to answer questions
        # that the evidence family does not cover.
        return []

    def run(self, query: str) -> OrchestratorResult:
        t0 = time.perf_counter()
        route = self.router.route(query)
        preflight = self.safety.review(query, "", [])
        if preflight.action in {SafetyAction.abstain, SafetyAction.escalate}:
            judge_result = self.judge.adjudicate([])
            latency_ms = (time.perf_counter() - t0) * 1000
            metrics = RunMetrics(
                architecture="paper_as_skill_deterministic_v0.3",
                latency_ms=round(latency_ms, 3),
                evidence_count=0,
                claim_count=0,
                coordination_messages=0,
                llm_calls=0,
            )
            return OrchestratorResult(
                query=query, route=route, selected_paper_ids=[], judge=judge_result, safety=preflight,
                answer=preflight.safe_message or "The system abstained.", provenance={}, metrics=metrics,
            )

        skills = self._retrieve(query)
        workspace = EvidenceWorkspace(query=query, skills=skills)
        draft = self.agents[route.agent].reason(workspace)
        target_population = self._target_population(query) if "generalized" in query.casefold() or "generalised" in query.casefold() else None
        judge_result = self.judge.adjudicate(workspace.claims, target_population=target_population)

        answer = draft.text + f"\n\nEvidence Judge: {judge_result.label.value}. {judge_result.rationale}"
        safety_result = self.safety.review(query, answer, workspace.claims)
        if safety_result.action in {SafetyAction.abstain, SafetyAction.escalate}:
            answer = safety_result.safe_message or "The system abstained."
        elif safety_result.action == SafetyAction.revise:
            answer += "\n\nSafety revision required: " + "; ".join(safety_result.reasons)

        provenance = {
            c.claim_id: [p.model_dump() for p in c.provenance]
            for c in workspace.claims
            if c.claim_id in draft.claim_ids
        }
        latency_ms = (time.perf_counter() - t0) * 1000
        metrics = RunMetrics(
            architecture="paper_as_skill_deterministic_v0.3",
            latency_ms=round(latency_ms, 3),
            evidence_count=len(skills),
            claim_count=len(workspace.claims),
            coordination_messages=0,
            llm_calls=0,
        )
        return OrchestratorResult(
            query=query, route=route, selected_paper_ids=[s.paper_id for s in skills],
            judge=judge_result, safety=safety_result, answer=answer, provenance=provenance, metrics=metrics,
        )
