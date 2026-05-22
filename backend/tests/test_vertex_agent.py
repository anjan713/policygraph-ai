import pytest

from app.services.vertex_agent import VertexAgent, VertexAgentError


def test_format_evidence_numbers_citations():
    citations = [
        {"page_number": 1, "excerpt": "MRI lumbar spine is covered after 6 weeks."},
        {"page_number": 2, "excerpt": "Prior authorization is required."},
    ]
    out = VertexAgent._format_evidence(citations, [])
    assert "[1] (page 1) MRI lumbar spine is covered after 6 weeks." in out
    assert "[2] (page 2) Prior authorization is required." in out


def test_format_evidence_includes_graph_context():
    citations = [{"page_number": 1, "excerpt": "policy text"}]
    graph = [{"procedure": "MRI lumbar spine", "relationship": "HAS_DECISION", "label": "covered"}]
    out = VertexAgent._format_evidence(citations, graph)
    assert "Knowledge-graph relationships" in out
    assert "MRI lumbar spine has decision covered" in out


def test_format_evidence_handles_no_evidence():
    assert VertexAgent._format_evidence([], []) == "(no evidence retrieved)"


def test_parse_json_plain_object():
    data = VertexAgent._parse_json('{"answer": "ok", "decision": "covered"}')
    assert data["answer"] == "ok"
    assert data["decision"] == "covered"


def test_parse_json_strips_markdown_fence():
    data = VertexAgent._parse_json('```json\n{"answer": "ok"}\n```')
    assert data["answer"] == "ok"


def test_parse_json_rejects_invalid():
    with pytest.raises(VertexAgentError):
        VertexAgent._parse_json("this is not json")


def test_parse_json_rejects_non_object():
    with pytest.raises(VertexAgentError):
        VertexAgent._parse_json("[1, 2, 3]")
