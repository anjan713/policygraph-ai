# RAG and Graph-RAG Pipeline

## Pipeline

1. PDF is rendered page-by-page with PyMuPDF.
2. PaddleOCR extracts text from every rendered page.
3. Text is chunked with overlap.
4. Each chunk is embedded using the local deterministic embedding service for the MVP.
5. Chunk embeddings are stored in PostgreSQL using pgvector.
6. Rule extraction creates structured policy requirements.
7. Neo4j graph nodes and relationships are created from documents, chunks, procedures, requirements, and decisions.
8. Query service embeds the user question and retrieves nearest chunks from pgvector.
9. Graph service expands context around the likely procedure.
10. Answer service returns a grounded answer with citations.

## Production upgrade

Replace `EmbeddingService` with Vertex AI embeddings. The database and retrieval contract remain the same.
