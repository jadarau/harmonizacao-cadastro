from __future__ import annotations
import json
import asyncio
from typing import Optional, Dict, Any

try:
    from aiokafka import AIOKafkaProducer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    AIOKafkaProducer = None  # type: ignore

from app.core.config import settings


class KafkaService:
    """Kafka producer service (lazy init)."""

    _instance: "KafkaService" | None = None

    def __init__(self) -> None:
        self._producer: Optional[Any] = None
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "KafkaService":
        if cls._instance is None:
            cls._instance = KafkaService()
        return cls._instance

    async def _ensure_started(self):
        if not settings.kafka_enabled:
            return
        if AIOKafkaProducer is None:
            # aiokafka not installed
            return
        if self._producer and self._producer._closed is False:
            return
        async with self._lock:
            if self._producer is None:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
            if self._producer._closed:  # type: ignore[attr-defined]
                await self._producer.start()
            else:
                await self._producer.start()

    async def send_cliente_event(self, cliente: Dict[str, Any]) -> None:
        """Send cliente event to Kafka if enabled."""
        if not settings.kafka_enabled:
            return
        if AIOKafkaProducer is None:
            return
        await self._ensure_started()
        assert self._producer is not None
        await self._producer.send_and_wait(settings.kafka_topic_cliente, cliente)

    async def close(self):
        if self._producer:
            await self._producer.stop()
