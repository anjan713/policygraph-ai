from app.services.embedding_service import EmbeddingService
from app.core.config import settings


def test_embed_returns_fixed_dimension_vector():
    vector = EmbeddingService().embed("MRI lumbar spine coverage criteria")
    assert len(vector) == settings.vector_dimension
    assert all(isinstance(value, float) for value in vector)


def test_embed_is_deterministic():
    service = EmbeddingService()
    assert service.embed("prior authorization") == service.embed("prior authorization")


def test_pgvector_literal_format():
    literal = EmbeddingService().to_pgvector_literal([0.5, -1.0])
    assert literal == "[0.50000000,-1.00000000]"
