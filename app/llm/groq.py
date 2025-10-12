from __future__ import annotations
import asyncio, json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List
import httpx
from fastapi import HTTPException
from app.core.config import settings

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