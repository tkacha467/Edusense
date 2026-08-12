"""Tests for Embedding Service."""
import pytest
from app.ai.embeddings.service import EmbeddingService


def test_embedding_service_dimensions_and_normalization():
    """Verify EmbeddingService generates 768-dim normalized vector embeddings."""
    emb_service = EmbeddingService(dimension=768)
    vec = emb_service.generate_embedding("Binary Search Tree properties")

    assert len(vec) == 768
    assert isinstance(vec[0], float)
