from __future__ import annotations
import asyncio, json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, Message, Choice, Usage

@dataclass
class _RetryPolicy:
    max_retries: int = 2
    base_delay: float = 0.5
    def schedule(self, attempt: int) -> float:
        return self.base_delay * (2 ** attempt) + (0.1 * attempt)

class GroqLlmClient:
    def __init__(self, *, api_key: str, base_url: str, timeout_s: float, max_retries: int) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._retry = _RetryPolicy(max_retries=max_retries)

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    @staticmethod
    def _to_openai_messages(messages: List[Message]) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def _req(self, payload: Dict[str, Any], *, stream: bool = False):
        url = f"{self._base_url}/chat/completions"
        attempt = 0
        while True:
            try:
                async with httpx.AsyncClient(timeout=self._timeout_s) as client:
                    if stream:
                        return client.stream("POST", url, headers=self._headers(), json=payload)
                    resp = await client.post(url, headers=self._headers(), json=payload)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if attempt >= self._retry.max_retries:
                    raise
                await asyncio.sleep(self._retry.schedule(attempt))
                attempt += 1

    async def chat(self, req: ChatRequest) -> ChatResponse:
        payload: Dict[str, Any] = {
            "model": req.model or settings.default_model,
            "messages": self._to_openai_messages(req.messages),
            "temperature": req.temperature,
        }
        if req.max_tokens is not None:
            payload["max_tokens"] = req.max_tokens
        data = await self._req(payload, stream=False)
        try:
            choices = [
                Choice(
                    index=i,
                    message=Message(
                        role=c.get("message", {}).get("role", "assistant"),
                        content=c.get("message", {}).get("content", ""),
                    ),
                    finish_reason=c.get("finish_reason"),
                )
                for i, c in enumerate(data.get("choices", []))
            ]
            usage = data.get("usage") or {}
            return ChatResponse(
                id=data.get("id", ""),
                created=data.get("created", int(datetime.utcnow().timestamp())),
                model=data.get("model", req.model or settings.default_model),
                choices=choices,
                usage=Usage(
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                ),
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Invalid response from LLM: {e}")

    async def chat_stream(self, req: ChatRequest) -> AsyncGenerator[str, None]:
        payload: Dict[str, Any] = {
            "model": req.model or settings.default_model,
            "messages": self._to_openai_messages(req.messages),
            "temperature": req.temperature,
            "stream": True,
        }
        if req.max_tokens is not None:
            payload["max_tokens"] = req.max_tokens
        async with await self._req(payload, stream=True) as rstream:
            async for line in rstream.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data_json = line[len("data: "):]
                    if data_json.strip() == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    try:
                        obj = json.loads(data_json)
                        delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield f"data: {json.dumps({'delta': delta})}\n\n"
                    except json.JSONDecodeError:
                        yield f"data: {json.dumps({'raw': data_json})}\n\n"