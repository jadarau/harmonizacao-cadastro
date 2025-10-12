from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from app.models import Cliente
from app.core.config import settings

class ClienteRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database[settings.mongodb_collection_clientes]
    
    async def create(self, cliente: Cliente) -> str:
        """Cria um novo cliente no banco de dados"""
        cliente_dict = cliente.dict()
        cliente_dict["created_at"] = datetime.utcnow()
        cliente_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(cliente_dict)
        return str(result.inserted_id)
    
    async def get_by_id(self, cliente_id: str) -> Optional[Cliente]:
        """Busca um cliente pelo ID"""
        try:
            object_id = ObjectId(cliente_id)
            cliente_data = await self.collection.find_one({"_id": object_id})
            
            if cliente_data:
                # Remove campos internos do MongoDB
                cliente_data.pop("_id", None)
                cliente_data.pop("created_at", None)
                cliente_data.pop("updated_at", None)
                return Cliente(**cliente_data)
            
            return None
        except Exception:
            return None
    
    async def get_by_email(self, email: str) -> Optional[Cliente]:
        """Busca um cliente pelo email"""
        cliente_data = await self.collection.find_one({"email": {"$in": [email]}})
        
        if cliente_data:
            cliente_data.pop("_id", None)
            cliente_data.pop("created_at", None)
            cliente_data.pop("updated_at", None)
            return Cliente(**cliente_data)
        
        return None
    
    async def get_by_telefone(self, telefone: str) -> Optional[Cliente]:
        """Busca um cliente pelo telefone"""
        cliente_data = await self.collection.find_one({"telefone": {"$in": [telefone]}})
        
        if cliente_data:
            cliente_data.pop("_id", None)
            cliente_data.pop("created_at", None)
            cliente_data.pop("updated_at", None)
            return Cliente(**cliente_data)
        
        return None
    
    async def update(self, cliente_id: str, cliente: Cliente) -> bool:
        """Atualiza um cliente existente"""
        try:
            object_id = ObjectId(cliente_id)
            cliente_dict = cliente.dict()
            cliente_dict["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": cliente_dict}
            )
            
            return result.modified_count > 0
        except Exception:
            return False
    
    async def delete(self, cliente_id: str) -> bool:
        """Remove um cliente do banco de dados"""
        try:
            object_id = ObjectId(cliente_id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Lista todos os clientes com paginação"""
        cursor = self.collection.find({}).skip(skip).limit(limit).sort("created_at", DESCENDING)
        clientes = []
        
        async for cliente_data in cursor:
            # Converte ObjectId para string
            cliente_data["id"] = str(cliente_data.pop("_id"))
            clientes.append(cliente_data)
        
        return clientes
    
    async def count(self) -> int:
        """Retorna o total de clientes"""
        return await self.collection.count_documents({})
    
    async def search_by_name(self, nome: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Busca clientes por nome (busca parcial)"""
        regex_pattern = {"$regex": nome, "$options": "i"}  # Case insensitive
        cursor = self.collection.find({"nome": regex_pattern}).skip(skip).limit(limit)
        
        clientes = []
        async for cliente_data in cursor:
            cliente_data["id"] = str(cliente_data.pop("_id"))
            clientes.append(cliente_data)
        
        return clientes
    
    async def create_indexes(self):
        """Cria índices para otimizar consultas"""
        await self.collection.create_index([("email", ASCENDING)])
        await self.collection.create_index([("telefone", ASCENDING)])
        await self.collection.create_index([("nome", ASCENDING)])
        await self.collection.create_index([("created_at", DESCENDING)])