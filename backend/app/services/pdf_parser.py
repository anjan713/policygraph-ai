from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
import re

from ..core.config import settings

class PdfParserError(RuntimeError):
    pass

class PdfParser:
    """PDF parser backed by PaddleOCR.

    The parser renders each PDF page to an image with PyMuPDF, then runs PaddleOCR
    over the rendered image. This handles both scanned PDFs and text-based PDFs with
    the same OCR path, which keeps the MVP aligned with open-source document OCR.
    """

    def __init__(self) -> None:
        self._ocr = None

    def _load_ocr(self):
        if self._ocr is not None:
            return self._ocr
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise PdfParserError(
                "PaddleOCR is not installed. Run `pip install -r backend/requirements.txt`. "
                "For Apple Silicon or CPU-only environments, follow the PaddleOCR install notes if wheel resolution fails."
            ) from exc

        # PaddleOCR 3.x and 2.x use slightly different constructor names. Try the newer
        # option first, then fall back to the widely used 2.x API.
        #
        # enable_mkldnn=False is required: paddlepaddle 3.x crashes during CPU inference
        # when the PIR executor lowers oneDNN ops (ConvertPirAttribute2RuntimeAttribute
        # not supported). Disabling oneDNN routes inference through the standard kernels.
        #
        # The doc-orientation, unwarping, and textline-orientation stages are disabled and
        # the lighter mobile detection model is used: PyMuPDF renders PDF pages upright and
        # flat, so those stages only add memory pressure and latency without improving OCR.
        try:
            self._ocr = PaddleOCR(
                lang=settings.paddleocr_lang,
                enable_mkldnn=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                text_detection_model_name="PP-OCRv5_mobile_det",
            )
        except TypeError:
            self._ocr = PaddleOCR(use_angle_cls=True, lang=settings.paddleocr_lang, enable_mkldnn=False)
        return self._ocr

    def extract_pages(self, path: Path) -> list[dict]:
        if not path.exists():
            raise PdfParserError(f"File not found: {path}")
        if path.suffix.lower() != ".pdf":
            raise PdfParserError("Only PDF files are supported.")

        try:
            import fitz  # PyMuPDF
        except ImportError as exc:
            raise PdfParserError("PyMuPDF is not installed. Run `pip install -r backend/requirements.txt`.") from exc

        ocr = self._load_ocr()
        pages: list[dict] = []
        try:
            doc = fitz.open(str(path))
            zoom = settings.ocr_render_dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            with TemporaryDirectory(prefix="policygraph_ocr_") as tmp:
                tmp_dir = Path(tmp)
                for index, page in enumerate(doc, start=1):
                    image_path = tmp_dir / f"page_{index}.png"
                    pix = page.get_pixmap(matrix=matrix, alpha=False)
                    pix.save(str(image_path))
                    text = self._run_ocr(ocr, image_path)
                    if text.strip():
                        pages.append({"page_number": index, "text": text.strip()})
        except PdfParserError:
            raise
        except Exception as exc:
            raise PdfParserError(f"Failed to parse PDF with PaddleOCR: {exc}") from exc

        if not pages:
            raise PdfParserError("PaddleOCR completed but no text was extracted from the PDF.")
        return pages

    def _run_ocr(self, ocr: Any, image_path: Path) -> str:
        # PaddleOCR 3.x often exposes predict(); 2.x exposes ocr(). Support both so
        # the project remains usable across current PaddleOCR releases.
        if hasattr(ocr, "predict"):
            result = ocr.predict(str(image_path))
        else:
            result = ocr.ocr(str(image_path), cls=True)
        return self._extract_text_from_result(result)

    def _extract_text_from_result(self, result: Any) -> str:
        lines: list[str] = []

        def walk(value: Any):
            if value is None:
                return
            if isinstance(value, dict):
                # Newer PaddleOCR result objects/dicts commonly expose rec_texts.
                rec_texts = value.get("rec_texts") or value.get("texts")
                if isinstance(rec_texts, list):
                    for item in rec_texts:
                        if isinstance(item, str) and item.strip():
                            lines.append(item.strip())
                for child in value.values():
                    walk(child)
                return
            if isinstance(value, str):
                if value.strip() and not re.fullmatch(r"[0-9.]+", value.strip()):
                    lines.append(value.strip())
                return
            if isinstance(value, (list, tuple)):
                # 2.x result shape includes [box, (text, score)] rows.
                if len(value) == 2 and isinstance(value[1], (list, tuple)) and value[1]:
                    maybe_text = value[1][0]
                    if isinstance(maybe_text, str) and maybe_text.strip():
                        lines.append(maybe_text.strip())
                for child in value:
                    walk(child)

        walk(result)
        # Preserve order while removing duplicates introduced by recursive parsing.
        seen = set()
        unique = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique.append(line)
        return "\n".join(unique)
