"""Embedding Service for generating text vector embeddings."""
import os
import logging
import numpy as np
from typing import List
from app.config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generates normalized vector embeddings for text documents."""

    def __init__(self, dimension: int = 768) -> None:
        self.dimension = dimension
        self.settings = get_settings()
        self.api_key = os.environ.get("GEMINI_API_KEY") or getattr(self.settings, "GEMINI_API_KEY", "")
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not configure genai for embeddings: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 768-dimensional normalized float embedding vector using Gemini.
        """
        try:
            import google.generativeai as genai
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.warning(f"Embedding failed, returning fallback vector: {e}")
            return [0.0] * self.dimension

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text chunks."""
        # Using loop since simple embed_content accepts single or batch, but loop is safer for fallback
        return [self.generate_embedding(t) for t in texts]
