"""Abstract base class for vector stores."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.document import DocumentChunk, SearchResult


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector store."""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        filter_metadata: Dict[str, Any] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar chunks."""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        pass
    
    @abstractmethod
    async def get_chunk(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a specific chunk by ID."""
        pass
    
    @abstractmethod
    async def list_documents(self) -> List[str]:
        """List all document IDs in the store."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        pass