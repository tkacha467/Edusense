"""Embedding Service for generating text vector embeddings."""
import hashlib
import numpy as np
from typing import List


class EmbeddingService:
    """Generates normalized vector embeddings for text documents."""

    def __init__(self, dimension: int = 768) -> None:
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a deterministic 768-dimensional normalized float embedding vector for text.
        """
        # Create deterministic pseudo-embedding vector from SHA256 hashes
        np.random.seed(int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16))
        vec = np.random.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text chunks."""
        return [self.generate_embedding(t) for t in texts]
