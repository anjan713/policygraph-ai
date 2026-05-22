from sqlalchemy import text
from ..db import db_connection, row_to_dict

class ValidationService:
    def validate(self, case: dict) -> dict:
        procedure = case.get("procedure", "").lower()
        with db_connection() as conn:
            rows = [row_to_dict(row) for row in conn.execute(text("""
                SELECT r.*, c.page_number, c.text AS chunk_text
                FROM rules r
                JOIN chunks c ON c.id = r.chunk_id
                WHERE lower(COALESCE(r.procedure, '')) LIKE :procedure OR lower(r.condition_text) LIKE :procedure
                ORDER BY r.confidence DESC
                LIMIT 10
            """), {"procedure": f"%{procedure}%"}).fetchall()]

        if not rows:
            return {"decision": "needs_review", "reasoning": "No matching extracted policy rule was found for the provided procedure.", "missing_fields": [], "matched_rules": []}

        missing = []
        if any("6 weeks" in (r.get("requirement_text") or "").lower() for r in rows) and case.get("conservative_treatment_weeks") is None:
            missing.append("conservative_treatment_weeks")
        if any("symptoms" in (r.get("requirement_text") or "").lower() for r in rows) and case.get("symptoms_persist") is None:
            missing.append("symptoms_persist")

        if missing:
            decision = "needs_review"
            reasoning = f"The policy appears to require additional case details: {', '.join(missing)}."
        else:
            weeks = case.get("conservative_treatment_weeks")
            symptoms = case.get("symptoms_persist")
            has_covered_rule = any(r["decision"] == "covered" for r in rows)
            if has_covered_rule and (weeks is None or weeks >= 6) and (symptoms is None or symptoms is True):
                decision = "likely_covered"
                reasoning = "The case appears to satisfy the extracted coverage requirements, including conservative treatment duration and persistent symptoms when required."
            elif any(r["decision"] == "not_covered" for r in rows):
                decision = "likely_not_covered"
                reasoning = "A matching extracted rule indicates the service may be not covered or excluded."
            else:
                decision = "needs_review"
                reasoning = "Matching rules were found, but the case does not clearly satisfy all extracted requirements."

        matched = [{"rule_id": r["id"], "procedure": r["procedure"], "decision": r["decision"], "requirement_text": r["requirement_text"], "condition_text": r["condition_text"], "confidence": r["confidence"], "page_number": r["page_number"], "excerpt": r["chunk_text"][:350]} for r in rows[:5]]
        return {"decision": decision, "reasoning": reasoning, "missing_fields": missing, "matched_rules": matched}
