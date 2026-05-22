from .db import init_db
from .services.document_processor import DocumentProcessor

def process_document_job(document_id: str) -> dict:
    init_db()
    return DocumentProcessor().process(document_id)
