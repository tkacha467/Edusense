"""Document Chunker for splitting text/markdown into text segments."""
import re
from typing import List, Dict, Any


class DocumentChunker:
    """Splits documents into overlapping chunks for RAG indexing."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        document_id: str,
        title: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Splits text into overlapping chunks with metadata.
        """
        # Clean text
        cleaned = re.sub(r'\s+', ' ', text).strip()
        chunks = []

        start = 0
        chunk_idx = 0

        while start < len(cleaned):
            end = min(start + self.chunk_size, len(cleaned))
            chunk_text = cleaned[start:end]

            chunks.append({
                "chunk_id": f"{document_id}_chunk_{chunk_idx}",
                "document_id": document_id,
                "title": title,
                "text": chunk_text,
                "start_char": start,
                "end_char": end
            })

            chunk_idx += 1
            start += (self.chunk_size - self.chunk_overlap)

        return chunks
