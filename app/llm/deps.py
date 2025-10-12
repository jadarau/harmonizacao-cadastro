from __future__ import annotations
from app.core.config import settings
from app.llm.groq import GroqLlmClient

async def get_llm_client():
    return GroqLlmClient(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        timeout_s=settings.request_timeout_s,
        max_retries=settings.max_retries,
    )