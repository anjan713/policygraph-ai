from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime, timezone
from sqlalchemy import text
from ..db import db_connection, row_to_dict
from ..schemas import DocumentResponse, DocumentListItem, EnqueueProcessResponse, DocumentStatusResponse, ProcessResponse
from ..services.storage_service import StorageService, StorageError
from ..services.job_queue import get_queue
from ..services.document_processor import DocumentProcessor

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse)
def upload_document(file: UploadFile = File(...)):
    storage = StorageService()
    try:
        document_id, storage_uri = storage.save_upload(file)
    except StorageError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    with db_connection() as conn:
        conn.execute(text("""
            INSERT INTO documents (id, file_name, storage_uri, status, created_at)
            VALUES (:id, :file_name, :storage_uri, :status, :created_at)
        """), {
            "id": document_id,
            "file_name": file.filename,
            "storage_uri": storage_uri,
            "status": "uploaded",
            "created_at": datetime.now(timezone.utc),
        })
    return DocumentResponse(document_id=document_id, file_name=file.filename, status="uploaded", storage_uri=storage_uri)

@router.get("", response_model=list[DocumentListItem])
def list_documents():
    with db_connection() as conn:
        rows = [row_to_dict(row) for row in conn.execute(text("SELECT * FROM documents ORDER BY created_at DESC")).fetchall()]
    return [DocumentListItem(**{**row, "created_at": row["created_at"].isoformat(), "processed_at": row["processed_at"].isoformat() if row.get("processed_at") else None}) for row in rows]

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(document_id: str):
    with db_connection() as conn:
        row = conn.execute(text("SELECT id, status, job_id, error_message, processed_at FROM documents WHERE id=:id"), {"id": document_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    data = row_to_dict(row)
    return DocumentStatusResponse(
        document_id=data["id"],
        status=data["status"],
        job_id=data.get("job_id"),
        error_message=data.get("error_message"),
        processed_at=data["processed_at"].isoformat() if data.get("processed_at") else None,
    )

@router.post("/{document_id}/process", response_model=EnqueueProcessResponse)
def enqueue_process_document(document_id: str):
    with db_connection() as conn:
        row = conn.execute(text("SELECT * FROM documents WHERE id=:id"), {"id": document_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")

    try:
        queue = get_queue()
        job = queue.enqueue(
            "app.jobs.process_document_job",
            document_id,
            job_timeout="45m",
            result_ttl=86400,
            failure_ttl=86400,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Redis/RQ is not available: {exc}") from exc

    with db_connection() as conn:
        conn.execute(text("UPDATE documents SET status='queued', job_id=:job_id, error_message=NULL WHERE id=:id"), {"id": document_id, "job_id": job.id})

    return EnqueueProcessResponse(document_id=document_id, status="queued", job_id=job.id, message="Document processing job queued. Poll /api/documents/{document_id}/status.")

@router.post("/{document_id}/process-sync", response_model=ProcessResponse)
def process_document_sync(document_id: str):
    """Developer-only convenience endpoint for local debugging without a worker."""
    try:
        return DocumentProcessor().process(document_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
