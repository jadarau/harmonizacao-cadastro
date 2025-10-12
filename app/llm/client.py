from __future__ import annotations
from typing import AsyncGenerator, Protocol
from app.schemas.chat import ChatRequest, ChatResponse

class LlmClient(Protocol):
    async def chat(self, req: ChatRequest) -> ChatResponse: ...
    async def chat_stream(self, req: ChatRequest) -> AsyncGenerator[str, None]: ...