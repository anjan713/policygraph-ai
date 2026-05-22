# Architecture Decisions

These are the current locked decisions for the project.

## 1. MVP workflow

The first version supports:

```text
Upload policy PDF -> PaddleOCR parse -> chunk -> vectorize -> build graph -> ask questions with citations
```


## 2. Storage

Use both storage modes:

- Local filesystem for local development cache.
- Google Cloud Storage for production-style GCP deployment.

The backend is the first upload path. Signed URLs can be added later for browser-direct uploads.

## 3. OCR

Always use PaddleOCR. We intentionally do not use a text-first shortcut because the project should prove scanned document support.

## 4. RAG architecture

Use full agentic Graph-RAG:

- OCR parser agent
- Chunking agent
- Rule extraction agent
- Embedding/indexing agent
- Graph builder agent
- Retrieval agent
- Graph expansion agent
- Citation agent
- Validation agent

## 5. Data layer

Use:

- PostgreSQL for metadata and policy records
- pgvector for chunk embeddings
- Neo4j for knowledge graph relationships
- Redis for background job queue and status
- GCS for PDF object storage

## 6. Processing model

Upload creates a document record and returns a document ID immediately. The user then enqueues background processing. The frontend polls status until the document is processed.
