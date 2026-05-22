# API Spec

Base URL: `http://localhost:8000`

## Health

```http
GET /health
```

Response:

```json
{"status":"ok"}
```

## Upload Document

```http
POST /api/documents/upload
Content-Type: multipart/form-data
```

Form field:

- `file`: PDF file

Response:

```json
{
  "document_id": "uuid",
  "file_name": "MRI_Coverage_Policy.pdf",
  "status": "uploaded",
  "storage_uri": "local://uploads/uuid.pdf"
}
```

## Process Document

```http
POST /api/documents/{document_id}/process
```

Response:

```json
{
  "document_id": "uuid",
  "status": "processed",
  "pages_extracted": 2,
  "chunks_created": 6,
  "rules_extracted": 4,
  "graph_nodes": 12,
  "graph_edges": 15
}
```

## List Documents

```http
GET /api/documents
```

## Ask Question

```http
POST /api/query
Content-Type: application/json
```

Request:

```json
{
  "question": "Is MRI lumbar spine covered after 6 weeks of conservative treatment?",
  "top_k": 5
}
```

Response:

```json
{
  "query_id": "uuid",
  "answer": "...",
  "confidence": 0.82,
  "citations": [
    {
      "document_id": "uuid",
      "chunk_id": "uuid",
      "page_number": 1,
      "excerpt": "..."
    }
  ]
}
```

## Validate Case

```http
POST /api/validate-case
Content-Type: application/json
```

Request:

```json
{
  "procedure": "MRI lumbar spine",
  "diagnosis": "lower back pain",
  "conservative_treatment_weeks": 6,
  "symptoms_persist": true
}
```

Response:

```json
{
  "decision": "likely_covered",
  "reasoning": "...",
  "missing_fields": [],
  "matched_rules": [...]
}
```

## Graph

```http
GET /api/graph
```

Returns graph nodes and edges.
