# OCR Pipeline

PolicyGraph AI uses PaddleOCR for PDF parsing.

## Why PaddleOCR

PaddleOCR is an open-source OCR/document parsing toolkit. In this project, it is used to parse uploaded healthcare policy PDFs before chunking, extraction, retrieval, and graph construction.

## Flow

```text
PDF upload
  -> store original PDF locally or in Google Cloud Storage
  -> render each PDF page to PNG with PyMuPDF
  -> run PaddleOCR on each page image
  -> normalize OCR text by page
  -> chunk text into policy sections
  -> extract rules
  -> build graph relationships
  -> answer questions with citations
```

## Parser implementation

File:

```text
backend/app/services/pdf_parser.py
```

The parser:

1. Opens the PDF using PyMuPDF.
2. Renders each page at `OCR_RENDER_DPI`.
3. Runs PaddleOCR against the rendered page image.
4. Extracts recognized text lines.
5. Returns structured page records:

```json
[
  {
    "page_number": 1,
    "text": "Coverage Policy: MRI Lumbar Spine..."
  }
]
```

## Environment variables

```bash
OCR_ENGINE=paddleocr
PADDLEOCR_LANG=en
OCR_RENDER_DPI=200
```

## Notes

- Use higher DPI for low-quality scans, such as `OCR_RENDER_DPI=250` or `300`.
- CPU mode is acceptable for an MVP, but OCR can be slow on large documents.
- For production, move OCR into an async worker or Cloud Run Job.
