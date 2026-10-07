from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    agent: str
    reason: str


class QueryRouter:
    selective_terms = {
        "adolescent", "adolescents", "youth", "student", "students", "older adult", "older adults",
        "elderly", "veteran", "veterans", "lgbtq", "subgroup",
    }
    indicated_terms = {
        "my risk", "my suicide", "me personally", "this patient", "this person",
        "postdischarge", "post-discharge", "self-harm", "suicide attempt"
    }

    def route(self, query: str) -> Route:
        q = query.casefold()
        if any(term in q for term in self.indicated_terms):
            return Route("Indicated", "query concerns indicated/high-risk or individual-level evidence")
        if any(term in q for term in self.selective_terms):
            return Route("Selective", "query concerns a specified subgroup")
        return Route("Universal", "query is population-level or general evidence synthesis")
