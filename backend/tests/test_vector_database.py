"""Tests for Vector Repository and ChromaDB integration."""
import pytest
from app.ai.retriever.chunker import DocumentChunker
from app.ai.retriever.search import VectorRepository


def test_vector_repository_add_and_search():
    """Verify adding chunks and top-k similarity search in VectorRepository."""
    vector_repo = VectorRepository()
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)

    chunks = chunker.chunk_text("Binary Search Tree operates in logarithmic time.", "doc_001", "BST Textbook")
    added = vector_repo.add_chunks(chunks)
    assert added >= 1

    results = vector_repo.search_similar("logarithmic time", top_k=1)
    assert len(results) >= 1
    assert "similarity_score" in results[0]
