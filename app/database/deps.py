from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.mongodb import get_database
from app.database.repository import ClienteRepository

async def get_cliente_repository() -> ClienteRepository:
    """Dependency injection para o repositório de clientes"""
    database: AsyncIOMotorDatabase = get_database()
    return ClienteRepository(database)