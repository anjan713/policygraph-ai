# GCP Services Used

This project is now GCP-first.

## Required for production-style deployment

| Service | Why it is used |
|---|---|
| Cloud Storage | Stores uploaded healthcare policy PDFs. |
| Cloud Run | Runs the FastAPI backend container and, optionally, a worker container. |
| Artifact Registry | Stores Docker images built for Cloud Run. |
| Cloud Build | Builds containers from source. |
| Cloud SQL for PostgreSQL | Stores documents, chunks, rules, queries, citations, and pgvector embeddings. |
| Memorystore for Redis | Provides Redis-compatible queue/status cache for background jobs. |
| Secret Manager | Stores database URLs, passwords, and runtime secrets. |
| IAM | Controls service account permissions for GCS, Cloud SQL, Cloud Run, and secrets. |

## Optional / upgrade services

| Service | Why it may be used later |
|---|---|
| Vertex AI | Replace local hashing embeddings with managed embeddings and Gemini generation. |
| Cloud Logging | Centralized logs for backend and worker containers. |
| Cloud Monitoring | Health checks, alerts, and metrics. |
| VPC Serverless Access / Direct VPC egress | Private access from Cloud Run to Cloud SQL, Memorystore, and Neo4j deployment if needed. |

## Important guardrail

Track created resources in `docs/GCP_RESOURCE_TRACKER.md`. That file is intentionally ignored by Git and should not be pushed to GitHub.
