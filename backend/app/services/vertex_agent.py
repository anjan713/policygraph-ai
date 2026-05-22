"""Vertex AI answer-generation agent for the Graph-RAG query pipeline.

The agent receives a user question together with the evidence gathered by the
rest of the pipeline — vector-retrieved policy chunks and knowledge-graph
context — and uses a Gemini model on Vertex AI to reason over that combined
evidence and produce a grounded answer, a coverage decision, and a confidence.

Authentication uses Application Default Credentials. On a GCP VM this resolves
to the attached service account via the metadata server, so no key file is
needed. When Vertex AI is disabled or a call fails, ``QueryService`` falls back
to the deterministic keyword composer, keeping the app usable offline.
"""

import json
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# Coverage vocabulary the agent must choose from — matches the rule extractor.
DECISIONS = ["covered", "not_covered", "requires_prior_authorization", "requires_review"]

SYSTEM_INSTRUCTION = """You are PolicyGraph AI, a healthcare policy coverage assistant.

Answer the user's question STRICTLY from the numbered policy evidence supplied in
the prompt. Follow these rules without exception:
- Never invent coverage criteria, requirements, exclusions, or decisions that are
  not present in the evidence.
- Ground every claim in the evidence and refer to it naturally
  (e.g. "the policy states...", "per the coverage criteria...").
- If the evidence does not clearly answer the question, choose the decision
  "requires_review" and explain what additional information would be needed.
- Keep the answer concise and clinical: 2-4 sentences.

Respond with ONLY a JSON object, no markdown fences, with exactly these keys:
{
  "answer": "<2-4 sentence grounded answer>",
  "decision": "<one of: covered | not_covered | requires_prior_authorization | requires_review>",
  "confidence": <number between 0 and 1>,
  "reasoning": "<one short sentence on why this decision follows from the evidence>"
}
"""


class VertexAgentError(RuntimeError):
    """Raised when the Vertex AI agent cannot produce an answer."""


class VertexAgent:
    """Gemini-on-Vertex-AI reasoning agent for grounded policy answers."""

    def __init__(self) -> None:
        self.enabled = settings.use_vertex_ai
        self.model = settings.vertex_llm_model
        self.location = settings.vertex_ai_location
        self.project = settings.google_cloud_project or settings.gcp_project_id
        self._client = None

    def is_available(self) -> bool:
        """Whether the agent is configured well enough to be attempted."""
        return self.enabled and bool(self.project)

    def status(self) -> dict:
        return {
            "enabled": self.enabled,
            "model": self.model,
            "location": self.location,
            "project": self.project,
        }

    def _client_or_raise(self):
        if self._client is not None:
            return self._client
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover - import guard
            raise VertexAgentError(
                "google-genai is not installed. Add it to requirements.txt."
            ) from exc
        if not self.project:
            raise VertexAgentError("GCP project is not configured (set GCP_PROJECT_ID).")
        self._client = genai.Client(vertexai=True, project=self.project, location=self.location)
        return self._client

    def answer(self, question: str, citations: list[dict], graph_context: list[dict]) -> dict:
        """Generate a grounded answer. Raises VertexAgentError on any failure."""
        client = self._client_or_raise()
        from google.genai import types

        prompt = (
            f"Question: {question}\n\n"
            f"Policy evidence:\n{self._format_evidence(citations, graph_context)}\n\n"
            "Answer the question using only the evidence above."
        )

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=settings.vertex_max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:  # network / quota / auth errors
            raise VertexAgentError(f"Vertex AI generate_content failed: {exc}") from exc

        text = (response.text or "").strip()
        if not text:
            finish = None
            try:
                finish = response.candidates[0].finish_reason
            except Exception:
                pass
            raise VertexAgentError(f"Gemini returned an empty response (finish_reason={finish}).")

        data = self._parse_json(text)
        decision = str(data.get("decision", "requires_review"))
        if decision not in DECISIONS:
            decision = "requires_review"
        try:
            confidence = float(data.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))

        answer_text = str(data.get("answer", "")).strip()
        if not answer_text:
            raise VertexAgentError("Gemini response did not contain an answer.")
        reasoning = str(data.get("reasoning", "")).strip()

        return {
            "answer": answer_text,
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "model": self.model,
        }

    @staticmethod
    def _parse_json(text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # Defensive: strip a stray markdown code fence if one appears.
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise VertexAgentError(f"Could not parse Gemini JSON output: {exc}") from exc
        if not isinstance(parsed, dict):
            raise VertexAgentError("Gemini JSON output was not an object.")
        return parsed

    @staticmethod
    def _format_evidence(citations: list[dict], graph_context: list[dict]) -> str:
        lines: list[str] = []
        for i, c in enumerate(citations, start=1):
            lines.append(f"[{i}] (page {c.get('page_number')}) {c.get('excerpt', '')}")
        if graph_context:
            lines.append("")
            lines.append("Knowledge-graph relationships for the relevant procedure:")
            for g in graph_context:
                procedure = g.get("procedure") or ""
                relationship = str(g.get("relationship") or "").replace("_", " ").lower()
                target = g.get("label") or g.get("text") or ""
                fact = f"- {procedure} {relationship} {target}".strip()
                if fact != "-":
                    lines.append(fact)
        return "\n".join(lines) if lines else "(no evidence retrieved)"
