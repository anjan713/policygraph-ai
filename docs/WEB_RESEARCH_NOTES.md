# Web Research Notes

Research-backed updates used for this GCP/PaddleOCR + full Graph-RAG version:

- PaddleOCR is the open-source OCR/document parsing engine selected for all PDF parsing in this project.
- Google Cloud Storage signed URLs provide time-limited access to specific storage resources, which is the recommended future upgrade for browser-direct PDF uploads.
- Cloud Run has official support/examples for deploying Python FastAPI services and is the target service for the backend container.
- Cloud SQL for PostgreSQL supports pgvector for storing, indexing, and querying embeddings directly in PostgreSQL.
- Memorystore for Redis is Google Cloud's managed Redis-compatible service and maps to the local Redis/RQ queue used by the worker.

Source references used while updating architecture:

- https://github.com/PaddlePaddle/PaddleOCR
- https://docs.cloud.google.com/storage/docs/access-control/signed-urls
- https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service
- https://docs.cloud.google.com/sql/docs/postgres/generate-manage-vector-embeddings
- https://docs.cloud.google.com/memorystore/docs/redis
