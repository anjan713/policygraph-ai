from app.services.normalization import normalize_text


def test_normalize_collapses_internal_whitespace():
    assert normalize_text("MRI   lumbar\n\tspine") == "MRI lumbar spine"


def test_normalize_strips_surrounding_whitespace():
    assert normalize_text("  prior authorization  ") == "prior authorization"


def test_normalize_handles_none_and_empty():
    assert normalize_text(None) == ""
    assert normalize_text("") == ""
