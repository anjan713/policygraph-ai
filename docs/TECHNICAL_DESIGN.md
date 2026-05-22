# Technical Design

## Architecture

```text
Next.js Frontend
  -> FastAPI Backend on Cloud Run/local Docker
    -> Google Cloud Storage/local filesystem for PDF storage
    -> Redis/RQ for background OCR jobs
    -> PaddleOCR parser
    -> Chunking + rule extraction agents
    -> PostgreSQL + pgvector for metadata and vector search
    -> Neo4j for Graph-RAG relationships
    -> Query service returns answers with citations and graph context
```

## Document lifecycle

1. Frontend uploads a PDF.
2. Backend stores the file locally and optionally uploads it to GCS.
3. Backend creates a `documents` row with status `uploaded`.
4. User clicks process.
5. Backend enqueues an RQ job in Redis and marks the document `queued`.
6. Worker changes status to `processing`.
7. Worker runs PaddleOCR, chunking, rule extraction, embeddings, pgvector inserts, and Neo4j graph creation.
8. Worker marks the document `processed` or `failed`.
9. Frontend polls `/api/documents/{document_id}/status`.

## Why this design

- PaddleOCR proves scanned-document support.
- PostgreSQL + pgvector keeps metadata and vectors together.
- Neo4j supports relationship-aware Graph-RAG.
- Redis avoids blocking upload requests during OCR.
- GCS matches production-style GCP object storage.
