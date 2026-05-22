from sklearn.feature_extraction.text import HashingVectorizer
from .normalization import normalize_text
from ..core.config import settings

class EmbeddingService:
    """Deterministic local embedding service for a working MVP.

    This stores real numeric vectors in pgvector without requiring an external paid
    model. For production, replace this class with Vertex AI text embeddings while
    keeping the same method contract.
    """

    def __init__(self) -> None:
        self.vectorizer = HashingVectorizer(
            n_features=settings.vector_dimension,
            alternate_sign=False,
            norm="l2",
            stop_words="english",
            ngram_range=(1, 2),
        )

    def embed(self, text: str) -> list[float]:
        matrix = self.vectorizer.transform([normalize_text(text)])
        arr = matrix.toarray()[0]
        return [float(x) for x in arr]

    def to_pgvector_literal(self, values: list[float]) -> str:
        return "[" + ",".join(f"{v:.8f}" for v in values) + "]"
