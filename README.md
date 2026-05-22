# PolicyGraph AI

PolicyGraph AI is a GCP-first healthcare policy intelligence project for **full agentic Graph-RAG** workflows.

This architecture is locked to the decisions below:

- **MVP workflow:** Upload policy PDF → PaddleOCR parse → chunk → ask questions with citations.
- **Storage:** Google Cloud Storage for production-style deployment, with local storage support for development cache.
- **OCR:** Always use open-source PaddleOCR for scanned and text-based PDFs.
- **RAG:** Full agentic Graph-RAG path with vector retrieval, graph expansion, and validation-ready rules.
- **Data stores:** PostgreSQL + pgvector, Neo4j, Redis.
- **Processing:** Upload returns a document ID; background worker processes OCR/chunking/rule extraction/graph creation; frontend polls document status.

## Local development

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
Frontend: http://localhost:3000
Backend docs: http://localhost:8000/docs
Neo4j Browser: http://localhost:7474
```

## Demo flow

1. Open the frontend upload page.
2. Upload `demo_files/MRI_Coverage_Policy.pdf`.
3. Click **Process in Background**.
4. Wait until status becomes `processed`.
5. Ask: `Is MRI lumbar spine covered after 6 weeks of conservative treatment?`
6. Validate a case with 6 weeks of conservative treatment and persistent symptoms.

## GCP development

```bash
gcloud auth application-default login
export GCP_PROJECT_ID=<your-project-id>
export GOOGLE_CLOUD_PROJECT=<your-project-id>
export GCP_REGION=us-central1
source scripts/use-gcp-dev.sh
```

Use GCS:

```bash
export USE_GCS=true
export GCS_BUCKET=<your-bucket-name>
```

## Important docs

- `docs/PRD.md`
- `docs/TECHNICAL_DESIGN.md`
- `docs/GCP_SERVICES.md`
- `docs/GCP_RESOURCE_TRACKER.md` — local/private guardrail file, intentionally ignored by Git
- `docs/OCR_PIPELINE.md`
- `docs/RAG_PIPELINE.md`
- `docs/LANGGRAPH_WORKFLOW.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `CLAUDE.md`

## Main APIs

```text
POST /api/documents/upload
POST /api/documents/{document_id}/process
GET  /api/documents/{document_id}/status
GET  /api/documents
POST /api/query
POST /api/validate-case
GET  /api/graph
```
