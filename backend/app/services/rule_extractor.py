import re
from uuid import uuid4
from datetime import datetime, timezone

PROCEDURE_PATTERNS = [
    r"MRI lumbar spine",
    r"MRI",
    r"prior authorization",
    r"HbA1c testing",
    r"diabetes care",
    r"claim review",
]

class RuleExtractor:
    def extract_rules(self, chunks: list[dict]) -> list[dict]:
        rules: list[dict] = []
        for chunk in chunks:
            sentences = re.split(r"(?<=[.!?])\s+", chunk["text"])
            for sentence in sentences:
                lower = sentence.lower()
                if not any(token in lower for token in ["covered", "requires", "required", "not covered", "prior authorization", "must", "eligible"]):
                    continue
                procedure = self._extract_procedure(sentence)
                decision = self._decision(sentence)
                requirement = self._requirement(sentence)
                rules.append({
                    "id": str(uuid4()),
                    "document_id": chunk["document_id"],
                    "chunk_id": chunk["id"],
                    "procedure": procedure,
                    "condition_text": sentence.strip(),
                    "requirement_text": requirement,
                    "decision": decision,
                    "confidence": self._confidence(sentence),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
        return rules

    def _extract_procedure(self, sentence: str) -> str | None:
        for pattern in PROCEDURE_PATTERNS:
            match = re.search(pattern, sentence, re.I)
            if match:
                return match.group(0)
        return None

    def _decision(self, sentence: str) -> str:
        lower = sentence.lower()
        if "not covered" in lower or "excluded" in lower:
            return "not_covered"
        if "prior authorization" in lower or "requires authorization" in lower:
            return "requires_prior_authorization"
        if "covered" in lower or "eligible" in lower:
            return "covered"
        return "requires_review"

    def _requirement(self, sentence: str) -> str | None:
        patterns = [
            r"6 weeks? of conservative treatment",
            r"symptoms? persist(?:s|ed)?",
            r"prior authorization",
            r"documentation of medical necessity",
            r"HbA1c testing every 3 months",
            r"provider documentation",
        ]
        found = [m.group(0) for p in patterns for m in re.finditer(p, sentence, re.I)]
        return "; ".join(dict.fromkeys(found)) if found else sentence.strip()

    def _confidence(self, sentence: str) -> float:
        lower = sentence.lower()
        score = 0.55
        for token in ["covered", "requires", "must", "not covered", "prior authorization"]:
            if token in lower:
                score += 0.08
        return min(score, 0.95)
