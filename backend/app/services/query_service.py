import logging
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import text
from ..db import db_connection
from .retrieval_service import RetrievalService
from .graph_service import GraphService
from .vertex_agent import VertexAgent, VertexAgentError

logger = logging.getLogger(__name__)

# How each detected decision is phrased back to the user (rule-based fallback).
DECISION_PHRASING = {
    "covered": "the service appears to be covered when the stated requirements are met",
    "not_covered": "the service appears to be not covered or excluded under the cited conditions",
    "requires_prior_authorization": "the service appears to require prior authorization",
    "requires_review": "the policy evidence is relevant but does not state a single clear coverage decision",
}

class QueryService:
    def __init__(self):
        self.retrieval = RetrievalService()
        self.graph = GraphService()
        self.agent = VertexAgent()

    def answer(self, question: str, top_k: int = 5) -> dict:
        chunks = self.retrieval.search(question, top_k=top_k)
        if not chunks:
            return {
                "query_id": str(uuid4()),
                "answer": "No processed policy evidence was found. Upload and process at least one policy PDF first.",
                "confidence": 0.0,
                "citations": [],
                "graph_context": [],
                "answer_mode": "no_evidence",
                "model": None,
            }

        query_id = str(uuid4())
        citations = []
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
            if not procedure_hint:
                with db_connection() as conn:
                    rule = conn.execute(text("SELECT procedure FROM rules WHERE chunk_id=:chunk_id AND procedure IS NOT NULL LIMIT 1"), {"chunk_id": chunk["id"]}).fetchone()
                    if rule:
                        procedure_hint = rule[0]

        graph_context = self.graph.related_context(procedure_hint)
        retrieval_confidence = min(0.95, sum(c["score"] for c in citations) / max(len(citations), 1) + 0.35)

        # Primary path: the Vertex AI Gemini agent reasons over the evidence.
        # Fallback path: the deterministic keyword composer keeps the app usable
        # when Vertex AI is disabled, misconfigured, or temporarily unavailable.
        answer = ""
        answer_mode = "rule_based"
        model = None
        if self.agent.is_available():
            try:
                result = self.agent.answer(question, citations, graph_context)
                answer = result["answer"]
                retrieval_confidence = result["confidence"]
                answer_mode = "vertex_gemini"
                model = result["model"]
            except VertexAgentError as exc:
                logger.warning("Vertex AI agent unavailable, using rule-based fallback: %s", exc)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Vertex AI agent error, using rule-based fallback: %s", exc)
        if not answer:
            answer = self._compose_answer(citations, graph_context, retrieval_confidence)

        confidence = retrieval_confidence
        with db_connection() as conn:
            conn.execute(text("INSERT INTO queries (id, question, answer, confidence, created_at) VALUES (:id, :question, :answer, :confidence, :created_at)"),
                        {"id": query_id, "question": question, "answer": answer, "confidence": confidence, "created_at": datetime.now(timezone.utc)})
            for citation in citations:
                conn.execute(text("""
                    INSERT INTO citations (id, query_id, document_id, chunk_id, page_number, excerpt)
                    VALUES (:id, :query_id, :document_id, :chunk_id, :page_number, :excerpt)
                """), {"id": str(uuid4()), "query_id": query_id, **citation})

        return {
            "query_id": query_id,
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
            "graph_context": graph_context,
            "answer_mode": answer_mode,
            "model": model,
        }

    def _classify_decision(self, text_value: str) -> str | None:
        """Classify a single piece of policy text into a coverage decision.

        Order matters: 'not covered' and 'excluded' are checked before the
        broader 'covered' token so a negation is never misread as approval.
        """
        lower = (text_value or "").lower()
        if "not covered" in lower or "excluded" in lower:
            return "not_covered"
        if "prior authorization" in lower or "requires authorization" in lower:
            return "requires_prior_authorization"
        if "covered" in lower or "eligible" in lower:
            return "covered"
        return None

    def _compose_answer(self, citations: list[dict], graph_context: list[dict], confidence: float) -> str:
        """Deterministic fallback answer built from the question-relevant excerpts.

        The decision is taken from the top-ranked citation excerpt — the sentence
        that best matches the question — rather than scanning the entire retrieved
        blob, so unrelated clauses elsewhere in the policy cannot flip the answer.
        """
        top = citations[0]
        decision = self._classify_decision(top["excerpt"])
        if decision is None:
            for citation in citations[1:]:
                decision = self._classify_decision(citation["excerpt"])
                if decision:
                    break
        decision = decision or "requires_review"

        phrasing = DECISION_PHRASING[decision]
        answer = (
            f"Based on the most relevant policy evidence (page {top['page_number']}), {phrasing}. "
            f"Confidence: {confidence:.2f}. Cited text: \"{top['excerpt']}\""
        )

        other_decisions = {
            g.get("label")
            for g in graph_context
            if g.get("node_type") == "CoverageDecision" and g.get("label") and g.get("label") != decision
        }
        if other_decisions:
            readable = ", ".join(sorted(d.replace("_", " ") for d in other_decisions))
            answer += f" Related policy rules for this procedure also mention: {readable}."
        return answer

    def _excerpt(self, text: str, question: str) -> str:
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        q_terms = {term.lower() for term in question.split() if len(term) > 3}
        if not sentences:
            return text[:500]
        ranked = sorted(sentences, key=lambda s: len(q_terms.intersection(set(s.lower().split()))), reverse=True)
        return ranked[0][:500]
