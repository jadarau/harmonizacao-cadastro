"""Dependencies for RAG-enhanced LLM client."""
from __future__ import annotations
from app.llm.rag_client import RAGLlmClient
from app.llm.deps import get_llm_client


async def get_rag_llm_client() -> RAGLlmClient:
    """Get RAG-enhanced LLM client instance."""
    base_client = await get_llm_client()
    return RAGLlmClient(base_client)