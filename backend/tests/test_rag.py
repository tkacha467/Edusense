"""Tests for RAG Retriever and RAG API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.ai.retriever.search import Retriever


def test_retriever_context_building():
    """Verify Retriever returns grounded context lines."""
    retriever = Retriever()
    context = retriever.retrieve_context("Data structures", top_k=2)
    assert isinstance(context, str)


def test_rag_api_endpoints(client: TestClient, admin_user, make_auth_header):
    """Verify /api/v1/rag/index and /api/v1/rag/search endpoints."""
    headers = make_auth_header(admin_user.firebase_uid)
    # Index document
    idx_payload = {
        "document_id": "doc_algo_101",
        "title": "Algorithms Chapter 1",
        "content": "Graph traversal algorithms include Breadth-First Search and Depth-First Search."
    }
    res_idx = client.post("/api/v1/rag/index", json=idx_payload, headers=headers)
    assert res_idx.status_code == 201
    assert res_idx.json()["chunks_indexed"] >= 1

    # Search vector store
    search_payload = {"query": "Breadth-First Search", "top_k": 2}
    res_search = client.post("/api/v1/rag/search", json=search_payload, headers=headers)
    assert res_search.status_code == 200
    assert "results" in res_search.json()
