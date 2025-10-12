"""Retrieval service for semantic search and document ranking."""
from __future__ import annotations
import time
from typing import List, Dict, Any
from app.rag.embeddings.service import get_embedding_service
from app.rag.vectorstore.factory import get_vector_store
from app.models.document import SearchResult


class RetrievalService:
    """Service for retrieving relevant documents based on queries."""
    
    def __init__(self):
        """Initialize retrieval service."""
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        min_score: float = 0.3,
        filter_metadata: Dict[str, Any] = None
    ) -> List[SearchResult]:
        """Search for relevant documents.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            min_score: Minimum relevance score threshold
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results ordered by relevance
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Search in vector store
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            limit=max_results,
            filter_metadata=filter_metadata,
            min_score=min_score
        )
        
        # Re-rank results (optional post-processing)
        ranked_results = await self._rerank_results(query, results)
        
        return ranked_results[:max_results]
    
    async def _rerank_results(
        self, 
        query: str, 
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """Re-rank search results using additional scoring methods.
        
        This method can implement more sophisticated ranking algorithms
        such as BM25, cross-encoder models, or hybrid scoring.
        
        Args:
            query: Original search query
            results: Initial search results from vector store
            
        Returns:
            Re-ranked search results
        """
        # For now, just return results as-is
        # In the future, you could implement:
        # 1. BM25 scoring for keyword matching
        # 2. Cross-encoder reranking
        # 3. Diversity scoring to avoid redundant results
        # 4. Freshness scoring based on document date
        
        return results
    
    async def get_context_for_query(
        self,
        query: str,
        max_chunks: int = 5,
        min_score: float = 0.3,
        max_context_length: int = 4000
    ) -> str:
        """Get concatenated context from relevant documents for RAG.
        
        Args:
            query: Search query
            max_chunks: Maximum number of chunks to include
            min_score: Minimum relevance score threshold
            max_context_length: Maximum total context length
            
        Returns:
            Concatenated context text
        """
        results = await self.search(
            query=query,
            max_results=max_chunks,
            min_score=min_score
        )
        
        if not results:
            return ""
        
        # Build context with source attribution
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results):
            # Add source information
            source_info = f"[Source {i+1}: {result.metadata.get('filename', 'Unknown')}]"
            chunk_text = f"{source_info}\n{result.content}\n"
            
            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_text) > max_context_length and context_parts:
                break
                
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n".join(context_parts)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get retrieval service statistics."""
        vector_stats = await self.vector_store.get_stats()
        
        return {
            "embedding_model": self.embedding_service.get_model_name(),
            "embedding_dimension": self.embedding_service.get_dimension(),
            "vector_store": vector_stats
        }


# Global retrieval service instance
_retrieval_service = None


def get_retrieval_service() -> RetrievalService:
    """Get the global retrieval service instance."""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service