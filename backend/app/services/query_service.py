from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import text
from ..db import db_connection
from .retrieval_service import RetrievalService
from .graph_service import GraphService

class QueryService:
    def __init__(self):
        self.retrieval = RetrievalService()
        self.graph = GraphService()

    def answer(self, question: str, top_k: int = 5) -> dict:
        chunks = self.retrieval.search(question, top_k=top_k)
        if not chunks:
            return {
                "query_id": str(uuid4()),
                "answer": "No processed policy evidence was found. Upload and process at least one policy PDF first.",
                "confidence": 0.0,
                "citations": [],
                "graph_context": [],
            }

        query_id = str(uuid4())
        citations = []
        evidence_lines = []
        procedure_hint = None
        for chunk in chunks:
            excerpt = self._excerpt(chunk["text"], question)
            citations.append({
                "document_id": chunk["document_id"],
                "chunk_id": chunk["id"],
                "page_number": chunk["page_number"],
                "excerpt": excerpt,
                "score": float(chunk["score"]),
            })
            evidence_lines.append(f"Page {chunk['page_number']}: {excerpt}")
            if not procedure_hint:
                with db_connection() as conn:
                    rule = conn.execute(text("SELECT procedure FROM rules WHERE chunk_id=:chunk_id AND procedure IS NOT NULL LIMIT 1"), {"chunk_id": chunk["id"]}).fetchone()
                    if rule:
                        procedure_hint = rule[0]

        graph_context = self.graph.related_context(procedure_hint)
        confidence = min(0.95, sum(c["score"] for c in citations) / max(len(citations), 1) + 0.35)
        answer = self._compose_answer(question, evidence_lines, graph_context, confidence)

        with db_connection() as conn:
            conn.execute(text("INSERT INTO queries (id, question, answer, confidence, created_at) VALUES (:id, :question, :answer, :confidence, :created_at)"),
                        {"id": query_id, "question": question, "answer": answer, "confidence": confidence, "created_at": datetime.now(timezone.utc)})
            for citation in citations:
                conn.execute(text("""
                    INSERT INTO citations (id, query_id, document_id, chunk_id, page_number, excerpt)
                    VALUES (:id, :query_id, :document_id, :chunk_id, :page_number, :excerpt)
                """), {"id": str(uuid4()), "query_id": query_id, **citation})

        return {"query_id": query_id, "answer": answer, "confidence": confidence, "citations": citations, "graph_context": graph_context}

    def _compose_answer(self, question: str, evidence_lines: list[str], graph_context: list[dict], confidence: float) -> str:
        joined = " ".join(evidence_lines)
        graph_text = " ".join([f"{g.get('procedure')} {g.get('relationship')} {g.get('label') or g.get('text')}" for g in graph_context])
        lower = f"{joined} {graph_text}".lower()
        if "not covered" in lower or "excluded" in lower:
            decision = "The policy evidence indicates this may be not covered or excluded."
        elif "prior authorization" in lower:
            decision = "The policy evidence indicates prior authorization may be required."
        elif "covered" in lower or "eligible" in lower:
            decision = "The policy evidence indicates this may be covered when the listed requirements are satisfied."
        else:
            decision = "The policy evidence is relevant, but a clear coverage decision needs review."
        graph_note = f" Graph context considered: {graph_text[:400]}" if graph_text else ""
        return f"{decision} Confidence: {confidence:.2f}. Supporting evidence: {joined[:1200]}{graph_note}"

    def _excerpt(self, text: str, question: str) -> str:
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        q_terms = {term.lower() for term in question.split() if len(term) > 3}
        if not sentences:
            return text[:500]
        ranked = sorted(sentences, key=lambda s: len(q_terms.intersection(set(s.lower().split()))), reverse=True)
        return ranked[0][:500]
