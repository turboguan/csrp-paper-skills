from __future__ import annotations

from collections.abc import Iterable

from .models import PaperSkill


def _contains(values: Iterable[str], query: str | None) -> bool:
    if query is None:
        return True
    q = query.casefold()
    return any(q in value.casefold() for value in values)


class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, PaperSkill] = {}

    def register(self, skill: PaperSkill, overwrite: bool = False) -> None:
        if skill.paper_id in self._skills and not overwrite:
            raise KeyError(f"paper_id already registered: {skill.paper_id}")
        self._skills[skill.paper_id] = skill

    def get(self, paper_id: str) -> PaperSkill:
        return self._skills[paper_id]

    def all(self) -> list[PaperSkill]:
        return list(self._skills.values())

    def search(
        self,
        text: str | None = None,
        population: str | None = None,
        intervention: str | None = None,
        outcome: str | None = None,
        study_type: str | None = None,
    ) -> list[PaperSkill]:
        results = []
        text_q = text.casefold() if text else None
        for skill in self._skills.values():
            haystack = " ".join(
                [skill.title, skill.abstract, *skill.population, *skill.intervention_or_exposure, *skill.outcomes]
            ).casefold()
            if text_q and not all(tok in haystack for tok in text_q.split() if len(tok) > 2):
                continue
            if not _contains(skill.population, population):
                continue
            if not _contains(skill.intervention_or_exposure, intervention):
                continue
            if not _contains(skill.outcomes, outcome):
                continue
            if study_type and study_type.casefold() not in skill.study_type.casefold():
                continue
            results.append(skill)
        return results

    def keyword_search(self, query: str, limit: int = 10) -> list[PaperSkill]:
        stopwords = {
            "what", "does", "about", "from", "with", "these", "those", "based",
            "synthetic", "evidence", "study", "studies", "findings", "consistent",
            "across", "say", "into", "this", "that", "were", "have", "been",
            "generalized", "generalised", "can", "the", "and", "for", "are",
            "population", "level", "prevention", "suicide", "strategy", "strategies",
            "represented", "types", "type", "hong", "kong", "available", "paper", "papers",
            "individual", "risk", "prediction", "without", "being", "used", "inform",
        }
        terms = []
        normalized = query.replace("/", " ").replace("-", " ")
        for raw in normalized.split():
            term = raw.casefold().strip("?,.;:()[]{}\"'")
            if len(term) >= 4 and term not in stopwords:
                terms.append(term)
        if not terms:
            return []

        scored: list[tuple[int, PaperSkill]] = []
        for skill in self._skills.values():
            high = " ".join([skill.paper_id, skill.title, *skill.intervention_or_exposure, *skill.outcomes]).casefold()
            topics = " ".join(str(x) for x in skill.metadata.get("topic_tags", [])).casefold()
            low = " ".join(
                [skill.abstract, skill.study_type, *skill.population, *skill.setting, *[c.statement for c in skill.evidence_claims]]
            ).casefold()
            score = sum(3 * high.count(term) + 2 * topics.count(term) + low.count(term) for term in terms)
            if score:
                scored.append((score, skill))
        if not scored:
            return []
        scored.sort(key=lambda x: (-x[0], x[1].paper_id))
        best = scored[0][0]
        threshold = max(1, int(best * 0.6))
        return [s for score, s in scored if score >= threshold][:limit]
