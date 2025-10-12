"""OpenAI embedding service implementation."""
from __future__ import annotations
import asyncio
from typing import List
import httpx
from app.rag.embeddings.base import EmbeddingService


class OpenAIEmbedding(EmbeddingService):
    """OpenAI embedding service."""
    
    def __init__(
        self, 
        api_key: str, 
        model_name: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1"
    ):
        """Initialize with OpenAI API credentials.
        
        Args:
            api_key: OpenAI API key
            model_name: OpenAI embedding model name
                       - "text-embedding-3-small" (1536 dim, cost-effective)
                       - "text-embedding-3-large" (3072 dim, highest quality)
                       - "text-embedding-ada-002" (1536 dim, legacy)
            base_url: OpenAI API base URL
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
        
        # Model dimensions mapping
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        response = await self.client.post(
            f"{self.base_url}/embeddings",
            json={
                "input": text,
                "model": self.model_name
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []
            
        response = await self.client.post(
            f"{self.base_url}/embeddings",
            json={
                "input": texts,
                "model": self.model_name
            }
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        return self._dimensions.get(self.model_name, 1536)
    
    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.model_name
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()