import re
from uuid import uuid4
from datetime import datetime, timezone

class Chunker:
    def __init__(self, max_words: int = 180, overlap_words: int = 35):
        self.max_words = max_words
        self.overlap_words = overlap_words

    def chunk_pages(self, document_id: str, pages: list[dict]) -> list[dict]:
        chunks = []
        for page in pages:
            text = re.sub(r"\s+", " ", page["text"]).strip()
            words = text.split()
            if not words:
                continue
            start = 0
            chunk_index = 0
            while start < len(words):
                end = min(start + self.max_words, len(words))
                chunk_text = " ".join(words[start:end])
                chunks.append({
                    "id": str(uuid4()),
                    "document_id": document_id,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "section_title": self._guess_section(chunk_text),
                    "text": chunk_text,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
                if end == len(words):
                    break
                start = max(0, end - self.overlap_words)
                chunk_index += 1
        return chunks

    def _guess_section(self, text: str) -> str:
        match = re.search(r"(Coverage Criteria|Medical Necessity|Prior Authorization|Exclusions|Claim Review|Diabetes Care|Policy Summary)", text, re.I)
        return match.group(1) if match else "General"
