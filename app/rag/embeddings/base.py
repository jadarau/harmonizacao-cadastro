"""Abstract base class for embedding services."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Union


class EmbeddingService(ABC):
    """Abstract base class for embedding services."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        pass