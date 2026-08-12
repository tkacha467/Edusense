"""Vector Repository and Retriever using ChromaDB and cosine similarity search."""
import os
import logging
import numpy as np
from typing import Any, Dict, List, Optional

from app.ai.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorRepository:
    """Vector database repository powered by ChromaDB with high-performance memory fallback."""

    def __init__(self, collection_name: str = "edusense_documents") -> None:
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()
        self.chroma_collection = None
        self.memory_store: List[Dict[str, Any]] = []
        self._init_chroma()

    def _init_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            client = chromadb.Client()
            self.chroma_collection = client.get_or_create_collection(self.collection_name)
            logger.info(f"Initialized ChromaDB collection '{self.collection_name}'")
        except Exception as e:
            logger.warning(f"Could not initialize ChromaDB: {e}. Using in-memory vector store.")

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Adds document chunks and embeddings to the vector repository."""
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.generate_batch_embeddings(texts)
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [{"document_id": c["document_id"], "title": c["title"]} for c in chunks]

        if self.chroma_collection:
            try:
                self.chroma_collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
            except Exception as e:
                logger.error(f"ChromaDB add exception: {e}")

        # Always update memory store for fallback
        for chunk, emb in zip(chunks, embeddings):
            self.memory_store.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "text": chunk["text"],
                "embedding": np.array(emb)
            })

        return len(chunks)

    def search_similar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Performs cosine similarity top-k retrieval for query."""
        query_emb = np.array(self.embedding_service.generate_embedding(query))

        if self.memory_store:
            # Cosine similarity calculation
            results = []
            for item in self.memory_store:
                doc_emb = item["embedding"]
                sim = float(np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb) + 1e-9))
                results.append({
                    "chunk_id": item["chunk_id"],
                    "document_id": item["document_id"],
                    "title": item["title"],
                    "text": item["text"],
                    "similarity_score": round(sim, 4)
                })

            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results[:top_k]

        return []


class Retriever:
    """RAG Retriever retrieving grounded context chunks for student queries."""

    def __init__(self, vector_repo: Optional[VectorRepository] = None) -> None:
        self.vector_repo = vector_repo or VectorRepository()

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves and formats top-k grounded context text."""
        chunks = self.vector_repo.search_similar(query, top_k=top_k)
        if not chunks:
            return "No specific document context found. Answering using core curriculum principles."

        context_lines = []
        for idx, c in enumerate(chunks, 1):
            context_lines.append(f"[{idx}] Source: {c['title']} (Score: {c['similarity_score']})\n{c['text']}")

        return "\n\n".join(context_lines)
