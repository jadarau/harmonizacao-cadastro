"""Embedding service factory and dependency injection."""
from __future__ import annotations
from typing import Optional
from app.rag.embeddings.base import EmbeddingService
from app.rag.embeddings.sentence_transformer import SentenceTransformerEmbedding
from app.rag.embeddings.openai import OpenAIEmbedding
from app.core.config import settings


class EmbeddingServiceFactory:
    """Factory for creating embedding services."""
    
    @staticmethod
    def create_service(
        service_type: str = "sentence_transformer",
        **kwargs
    ) -> EmbeddingService:
        """Create an embedding service.
        
        Args:
            service_type: Type of service ("sentence_transformer", "openai")
            **kwargs: Additional arguments for the service
        """
        if service_type == "sentence_transformer":
            model_name = kwargs.get("model_name", "all-MiniLM-L6-v2")
            return SentenceTransformerEmbedding(model_name=model_name)
        elif service_type == "openai":
            api_key = kwargs.get("api_key") or getattr(settings, "openai_api_key", None)
            if not api_key:
                raise ValueError("OpenAI API key is required for OpenAI embedding service")
            model_name = kwargs.get("model_name", "text-embedding-3-small")
            base_url = kwargs.get("base_url", "https://api.openai.com/v1")
            return OpenAIEmbedding(api_key=api_key, model_name=model_name, base_url=base_url)
        else:
            raise ValueError(f"Unknown embedding service type: {service_type}")


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        # Default to sentence transformer for local deployment
        _embedding_service = EmbeddingServiceFactory.create_service("sentence_transformer")
    return _embedding_service


def set_embedding_service(service: EmbeddingService):
    """Set the global embedding service instance."""
    global _embedding_service
    _embedding_service = service