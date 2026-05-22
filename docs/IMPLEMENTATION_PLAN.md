# Implementation Plan

## Phase 1 — Foundation

1. Add Docker Compose services for PostgreSQL/pgvector, Redis, Neo4j, backend, worker, and frontend.
2. Configure FastAPI environment variables for GCP, PostgreSQL, Redis, Neo4j, and PaddleOCR.
3. Add `.gitignore` guardrail for local GCP resource tracker and credentials.

## Phase 2 — Document Upload and Storage

1. Add PDF upload endpoint.
2. Store uploaded files locally.
3. Add optional Google Cloud Storage upload.
4. Create document metadata rows in PostgreSQL.

## Phase 3 — Background Processing

1. Add Redis/RQ queue.
2. Add worker process.
3. Add document status endpoint.
4. Add frontend polling.

## Phase 4 — OCR and Indexing

1. Render PDF pages with PyMuPDF.
2. Run PaddleOCR on every page.
3. Chunk extracted text.
4. Embed chunks and store vectors in pgvector.

## Phase 5 — Graph-RAG

1. Extract structured rules.
2. Create Neo4j nodes and relationships.
3. Query pgvector for relevant chunks.
4. Expand with graph context.
5. Return citations and confidence.

## Phase 6 — Guardrails and Cloud Tracking

1. Maintain `docs/GCP_RESOURCE_TRACKER.md` locally.
2. Do not commit resource tracker or credentials.
3. Track all created GCP resources and cleanup commands.
