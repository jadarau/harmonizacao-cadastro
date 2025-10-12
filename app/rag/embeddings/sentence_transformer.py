"""Sentence Transformers embedding service implementation."""
from __future__ import annotations
import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from app.rag.embeddings.base import EmbeddingService


class SentenceTransformerEmbedding(EmbeddingService):
    """Sentence Transformers embedding service."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with specified model.
        
        Args:
            model_name: Name of the sentence transformer model to use.
                       Popular options:
                       - "all-MiniLM-L6-v2" (384 dim, fast, good for general use)
                       - "all-mpnet-base-v2" (768 dim, higher quality)
                       - "multi-qa-MiniLM-L6-cos-v1" (384 dim, good for Q&A)
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, 
            lambda: self.model.encode(text, convert_to_tensor=False)
        )
        return embedding.tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []
            
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        )
        return [emb.tolist() for emb in embeddings]
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.model_name