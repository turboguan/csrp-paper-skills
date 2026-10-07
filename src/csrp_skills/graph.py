from __future__ import annotations

from itertools import combinations

import networkx as nx

from .models import Direction, EvidenceClaim, PaperSkill


def norm(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


class EvidenceGraph:
    def __init__(self):
        self.g = nx.MultiDiGraph()
        self.claim_index: dict[str, EvidenceClaim] = {}

    def build_graph(self, skills: list[PaperSkill]) -> "EvidenceGraph":
        self.g.clear()
        self.claim_index.clear()
        for skill in skills:
            p = f"paper:{skill.paper_id}"
            self.g.add_node(p, node_type="Paper", label=skill.title, paper_id=skill.paper_id)
            for claim in skill.evidence_claims:
                c = f"claim:{claim.claim_id}"
                self.claim_index[claim.claim_id] = claim
                self.g.add_node(c, node_type="Claim", label=claim.statement, claim_id=claim.claim_id)
                self.g.add_edge(p, c, relation="HAS_CLAIM")
                self._attach_entity(c, "Population", claim.population, "STUDIES_POPULATION")
                self._attach_entity(c, "Intervention", claim.intervention_or_exposure, "TESTS_INTERVENTION")
                self._attach_entity(c, "Outcome", claim.outcome, "MEASURES_OUTCOME")
                self._attach_entity(c, "Method", claim.method, "USES_METHOD")
        known = {skill.paper_id for skill in skills}
        for skill in skills:
            for related_id in skill.related_papers:
                if related_id in known:
                    self.g.add_edge(f"paper:{skill.paper_id}", f"paper:{related_id}", relation="RELATED_TO")
        self._infer_claim_relations()
        return self

    def _attach_entity(self, claim_node: str, entity_type: str, value: str | None, relation: str) -> None:
        if not value:
            return
        node = f"{entity_type.lower()}:{norm(value)}"
        self.g.add_node(node, node_type=entity_type, label=value)
        self.g.add_edge(claim_node, node, relation=relation)

    def _infer_claim_relations(self) -> None:
        for a, b in combinations(self.claim_index.values(), 2):
            if not a.intervention_or_exposure or not b.intervention_or_exposure or not a.outcome or not b.outcome:
                continue
            same_intervention = norm(a.intervention_or_exposure) == norm(b.intervention_or_exposure)
            same_outcome = norm(a.outcome) == norm(b.outcome)
            if not (same_intervention and same_outcome):
                continue
            same_population = norm(a.population) == norm(b.population)
            same_method = norm(a.method) == norm(b.method)
            comparable = same_population and same_method
            opposing = {a.direction, b.direction} == {Direction.beneficial, Direction.harmful}
            same_direction = a.direction == b.direction and a.direction not in {Direction.descriptive, Direction.mixed}
            if comparable and opposing:
                rel = "CONTRADICTS"
            elif comparable and same_direction:
                rel = "SUPPORTS"
            else:
                rel = "QUALIFIES"
            self.g.add_edge(f"claim:{a.claim_id}", f"claim:{b.claim_id}", relation=rel)
            self.g.add_edge(f"claim:{b.claim_id}", f"claim:{a.claim_id}", relation=rel)

    def query_related_claims(
        self, population: str | None = None, intervention: str | None = None, outcome: str | None = None
    ) -> list[EvidenceClaim]:
        claims = []
        for claim in self.claim_index.values():
            if population and norm(population) not in norm(claim.population):
                continue
            if intervention and norm(intervention) not in norm(claim.intervention_or_exposure):
                continue
            if outcome and norm(outcome) not in norm(claim.outcome):
                continue
            claims.append(claim)
        return claims

    def relation_between(self, claim_a: str, claim_b: str) -> list[str]:
        u, v = f"claim:{claim_a}", f"claim:{claim_b}"
        if not self.g.has_edge(u, v):
            return []
        return [d["relation"] for d in self.g.get_edge_data(u, v).values()]

    def find_conflicts(self) -> list[tuple[str, str]]:
        pairs = []
        seen = set()
        for u, v, data in self.g.edges(data=True):
            if data.get("relation") != "CONTRADICTS":
                continue
            a, b = u.removeprefix("claim:"), v.removeprefix("claim:")
            key = tuple(sorted((a, b)))
            if key not in seen:
                seen.add(key)
                pairs.append(key)
        return pairs
