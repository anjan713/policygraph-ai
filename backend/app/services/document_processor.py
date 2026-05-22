from datetime import datetime, timezone
from sqlalchemy import text
from ..db import db_connection, row_to_dict
from .storage_service import StorageService, StorageError
from .pdf_parser import PdfParser, PdfParserError
from .chunker import Chunker
from .rule_extractor import RuleExtractor
from .embedding_service import EmbeddingService
from .graph_service import GraphService

class DocumentProcessor:
    def process(self, document_id: str) -> dict:
        with db_connection() as conn:
            row = conn.execute(text("SELECT * FROM documents WHERE id=:id"), {"id": document_id}).fetchone()
            if not row:
                raise ValueError(f"Document not found: {document_id}")
            document = row_to_dict(row)
            conn.execute(text("UPDATE documents SET status='processing', error_message=NULL WHERE id=:id"), {"id": document_id})

        storage = StorageService()
        parser = PdfParser()
        chunker = Chunker()
        extractor = RuleExtractor()
        embedder = EmbeddingService()
        graph = GraphService()

        try:
            local_path = storage.resolve_local_path(document["storage_uri"])
            pages = parser.extract_pages(local_path)
            chunks = chunker.chunk_pages(document_id, pages)
            rules = extractor.extract_rules(chunks)
            for chunk in chunks:
                chunk["embedding"] = embedder.to_pgvector_literal(embedder.embed(chunk["text"]))

            with db_connection() as conn:
                conn.execute(text("DELETE FROM rules WHERE document_id=:id"), {"id": document_id})
                conn.execute(text("DELETE FROM chunks WHERE document_id=:id"), {"id": document_id})
                for chunk in chunks:
                    conn.execute(text("""
                        INSERT INTO chunks (id, document_id, page_number, chunk_index, section_title, text, embedding, created_at)
                        VALUES (:id, :document_id, :page_number, :chunk_index, :section_title, :text, CAST(:embedding AS vector), :created_at)
                    """), chunk)
                for rule in rules:
                    conn.execute(text("""
                        INSERT INTO rules (id, document_id, chunk_id, procedure, condition_text, requirement_text, decision, confidence, created_at)
                        VALUES (:id, :document_id, :chunk_id, :procedure, :condition_text, :requirement_text, :decision, :confidence, :created_at)
                    """), rule)
                conn.execute(text("""
                    UPDATE documents SET status='processed', processed_at=:processed_at, error_message=NULL WHERE id=:id
                """), {"id": document_id, "processed_at": datetime.now(timezone.utc)})

            node_count, edge_count = graph.build_from_rules(document, chunks, rules)
            return {
                "document_id": document_id,
                "status": "processed",
                "pages_extracted": len(pages),
                "chunks_created": len(chunks),
                "rules_extracted": len(rules),
                "graph_nodes": node_count,
                "graph_edges": edge_count,
            }
        except Exception as exc:
            with db_connection() as conn:
                conn.execute(text("UPDATE documents SET status='failed', error_message=:err WHERE id=:id"), {"id": document_id, "err": str(exc)[:1000]})
            raise
