def test_true_conflict_detected(graph):
    assert ("SYN-004-C1", "SYN-005-C1") in graph.find_conflicts()


def test_method_difference_is_qualification(graph):
    rels = graph.relation_between("SYN-001-C1", "SYN-002-C1")
    assert "QUALIFIES" in rels
    assert "CONTRADICTS" not in rels
