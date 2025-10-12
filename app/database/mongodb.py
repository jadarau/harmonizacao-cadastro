from __future__ import annotations
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

# Instância global do MongoDB
mongodb = MongoDB()

async def connect_to_mongo():
    """Conecta ao MongoDB"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb.database = mongodb.client[settings.mongodb_database]
        
        # Testa a conexão
        await mongodb.client.admin.command('ping')
        logger.info(f"Conectado ao MongoDB: {settings.mongodb_database}")
        
    except Exception as e:
        logger.error(f"Erro ao conectar ao MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Fecha a conexão com MongoDB"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Conexão com MongoDB fechada")

def get_database() -> AsyncIOMotorDatabase:
    """Retorna a instância do banco de dados"""
    return mongodb.database