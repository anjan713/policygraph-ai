from app.services.chunker import Chunker
from app.services.rule_extractor import RuleExtractor


def test_chunker_and_rule_extractor_extracts_coverage_rule():
    pages = [{"page_number": 1, "text": "Coverage Criteria. MRI lumbar spine is covered when symptoms persist after 6 weeks of conservative treatment."}]
    chunks = Chunker(max_words=40, overlap_words=5).chunk_pages("doc1", pages)
    rules = RuleExtractor().extract_rules(chunks)
    assert len(chunks) == 1
    assert rules
    assert rules[0]["decision"] == "covered"
    assert "6 weeks" in rules[0]["requirement_text"]
