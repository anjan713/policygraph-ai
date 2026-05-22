from sqlalchemy import text
from ..db import db_connection, row_to_dict
from .embedding_service import EmbeddingService

class RetrievalService:
    def __init__(self) -> None:
        self.embedder = EmbeddingService()

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        vector_literal = self.embedder.to_pgvector_literal(self.embedder.embed(question))
        with db_connection() as conn:
            rows = conn.execute(text("""
                SELECT id, document_id, page_number, chunk_index, section_title, text,
                       1 - (embedding <=> CAST(:embedding AS vector)) AS score
                FROM chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """), {"embedding": vector_literal, "top_k": top_k}).fetchall()
        return [row_to_dict(row) for row in rows if row_to_dict(row).get("score", 0) is not None]
