from __future__ import annotations
import json
import logging
from typing import Optional

from app.core.config import settings

try:
    # Import lazily to avoid hard dependency when disabled
    from aiokafka import AIOKafkaProducer  # type: ignore
except Exception:  # pragma: no cover - environment without aiokafka
    AIOKafkaProducer = None  # type: ignore

logger = logging.getLogger(__name__)

_producer: Optional[object] = None


async def start_kafka_producer() -> None:
    """Inicializa o produtor Kafka se habilitado."""
    global _producer
    if not settings.kafka_enabled:
        logger.info("Kafka desabilitado por configuração. Pulando inicialização do produtor.")
        return
    if AIOKafkaProducer is None:
        logger.warning("aiokafka não está instalado. Defina KAFKA_ENABLED=false ou instale a dependência.")
        return
    if _producer is not None:
        return

    try:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: (str(v).encode("utf-8") if v is not None else None),
        )
        await _producer.start()
        logger.info("Produtor Kafka iniciado.")
    except Exception as e:
        logger.error(f"Falha ao iniciar produtor Kafka: {e}")
        _producer = None


async def stop_kafka_producer() -> None:
    """Encerra o produtor Kafka se existe."""
    global _producer
    if _producer is not None:
        try:
            await _producer.stop()
            logger.info("Produtor Kafka finalizado.")
        except Exception as e:
            logger.warning(f"Erro ao finalizar produtor Kafka: {e}")
        finally:
            _producer = None


async def send_cliente_event(cliente: dict) -> None:
    """Envia evento do cliente para o tópico configurado.

    Ignora silenciosamente se Kafka estiver desabilitado ou indisponível.
    """
    if not settings.kafka_enabled:
        return
    if _producer is None:
        logger.debug("Produtor Kafka não iniciado. Evento não enviado.")
        return

    try:
        key = cliente.get("cliente_id") or cliente.get("id") or None
        await _producer.send_and_wait(settings.kafka_topic_cliente, key=key, value=cliente)
        logger.debug("Evento de cliente enviado ao Kafka.")
    except Exception as e:
        # Não interromper o fluxo da API por falha de evento
        logger.warning(f"Falha ao enviar evento de cliente ao Kafka: {e}")
