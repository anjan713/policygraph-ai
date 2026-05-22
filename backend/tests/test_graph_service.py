from app.services.graph_service import GraphService


def test_node_id_is_deterministic():
    first = GraphService._node_id("requirement", "6 weeks conservative treatment")
    second = GraphService._node_id("requirement", "6 weeks conservative treatment")
    assert first == second


def test_node_id_varies_by_type_and_value():
    base = GraphService._node_id("requirement", "6 weeks conservative treatment")
    assert GraphService._node_id("requirement", "symptoms persist") != base
    assert GraphService._node_id("decision", "6 weeks conservative treatment") != base
