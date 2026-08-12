"""RAG & Vector Database REST API router."""
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.retriever.chunker import DocumentChunker
from app.ai.retriever.search import VectorRepository
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/rag", tags=["RAG Vector Engine"])

def get_vector_repo() -> VectorRepository:
    return VectorRepository()

def get_chunker() -> DocumentChunker:
    return DocumentChunker()


class IndexDocumentInput(BaseModel):
    document_id: str = Field(..., description="Unique document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Raw text or markdown document content")

class SearchVectorInput(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Top-K results count")


@router.post("/index", status_code=status.HTTP_201_CREATED)
def index_document(
    input_data: IndexDocumentInput,
    current_user: User = Depends(get_current_user),
    vector_repo: VectorRepository = Depends(get_vector_repo),
    chunker: DocumentChunker = Depends(get_chunker)
) -> Any:
    """Chunks text document and indexes embeddings into ChromaDB vector repository."""
    chunks = chunker.chunk_text(
        text=input_data.content,
        document_id=input_data.document_id,
        title=input_data.title
    )
    added_count = vector_repo.add_chunks(chunks)
    return {
        "status": "success",
        "document_id": input_data.document_id,
        "chunks_indexed": added_count
    }


@router.post("/search")
def search_vector_store(
    input_data: SearchVectorInput,
    current_user: User = Depends(get_current_user),
    vector_repo: VectorRepository = Depends(get_vector_repo)
) -> Any:
    """Performs top-k vector similarity search over indexed document chunks."""
    results = vector_repo.search_similar(
        query=input_data.query,
        top_k=input_data.top_k or 3
    )
    return {
        "query": input_data.query,
        "results_count": len(results),
        "results": results
    }
