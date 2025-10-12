"""Vector store factory and dependency injection."""
from __future__ import annotations
from typing import Optional
from app.rag.vectorstore.base import VectorStore
from app.rag.vectorstore.chroma import ChromaVectorStore


class VectorStoreFactory:
    """Factory for creating vector stores."""
    
    @staticmethod
    def create_store(
        store_type: str = "chroma",
        **kwargs
    ) -> VectorStore:
        """Create a vector store.
        
        Args:
            store_type: Type of store ("chroma", "faiss")
            **kwargs: Additional arguments for the store
        """
        if store_type == "chroma":
            collection_name = kwargs.get("collection_name", "harmonizacao_docs")
            persist_directory = kwargs.get("persist_directory", "./data/vectorstore/chroma")
            return ChromaVectorStore(
                collection_name=collection_name,
                persist_directory=persist_directory
            )
        else:
            raise ValueError(f"Unknown vector store type: {store_type}")


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreFactory.create_store("chroma")
    return _vector_store


def set_vector_store(store: VectorStore):
    """Set the global vector store instance."""
    global _vector_store
    _vector_store = store