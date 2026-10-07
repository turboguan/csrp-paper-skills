def test_structured_filter(registry):
    hits = registry.search(population="adolescents", outcome="suicidal ideation")
    assert {x.paper_id for x in hits} == {"SYN-001", "SYN-002"}


def test_exact_get(registry):
    assert registry.get("SYN-004").title.startswith("Synthetic interrupted")
