from app.services.pdf_parser import PdfParser


def _extract(result):
    # _extract_text_from_result is pure; it does not require a loaded OCR engine.
    return PdfParser()._extract_text_from_result(result)


def test_extracts_paddleocr_3x_rec_texts():
    # PaddleOCR 3.x predict() returns result objects exposing rec_texts.
    result = [{"rec_texts": ["Coverage Policy", "MRI lumbar spine"]}]
    assert _extract(result) == "Coverage Policy\nMRI lumbar spine"


def test_extracts_paddleocr_2x_line_tuples():
    # PaddleOCR 2.x ocr() returns [box, (text, score)] rows per page.
    box = [[0, 0], [10, 0], [10, 5], [0, 5]]
    result = [[[box, ("Prior authorization required", 0.98)]]]
    assert _extract(result) == "Prior authorization required"


def test_ignores_result_metadata_and_dedupes():
    # A 3.x result object also carries metadata such as input_path; only the
    # recognized rec_texts must be returned, and duplicate lines collapsed.
    result = [{
        "input_path": "/tmp/policygraph_ocr_abcd/page_1.png",
        "page_index": 0,
        "rec_texts": ["Coverage Criteria", "Coverage Criteria", "Prior authorization required"],
    }]
    assert _extract(result) == "Coverage Criteria\nPrior authorization required"
