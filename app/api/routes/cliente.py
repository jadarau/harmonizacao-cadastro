from __future__ import annotations
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Cliente
from app.database.deps import get_cliente_repository
from app.database.repository import ClienteRepository
from app.services.rag_service import RAGService

router = APIRouter(prefix="/v1/cliente", tags=["cliente"])

@router.post("/formulario", status_code=201)
async def receber_formulario(
    cliente: Cliente,
    repository: ClienteRepository = Depends(get_cliente_repository),
    rag_service: RAGService = Depends(lambda: RAGService())
):
    """
    Rota para receber dados de um formulário web com informações do cliente
    """
    try:
        # Verifica se já existe cliente com o mesmo email
        for email in cliente.email:
            existing_cliente = await repository.get_by_email(email)
            if existing_cliente:
                raise HTTPException(
                    status_code=409,
                    detail=f"Cliente com email {email} já existe"
                )
        
        # Verifica se já existe cliente com o mesmo telefone
        for telefone in cliente.telefone:
            existing_cliente = await repository.get_by_telefone(telefone)
            if existing_cliente:
                raise HTTPException(
                    status_code=409,
                    detail=f"Cliente com telefone {telefone} já existe"
                )
        
        # Classifica o cliente usando o RAG antes de salvar
        classificacao = rag_service.classificar_cliente(cliente.dict())
        cliente_dict = cliente.dict()
        cliente_dict["classificacao_rag"] = classificacao

        # Salva o cliente no banco de dados (com classificação)
        cliente_id = await repository.create(Cliente(**cliente_dict))

        return {
            "status": "success",
            "message": "Cliente criado com sucesso",
            "cliente_id": cliente_id,
            "cliente": cliente_dict,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/healthz")
async def health():
    """Endpoint de health check para rotas de cliente"""
    return {"status": "ok", "service": "cliente", "time": datetime.utcnow().isoformat()}

@router.get("/{cliente_id}")
async def get_cliente(
    cliente_id: str,
    repository: ClienteRepository = Depends(get_cliente_repository)
):
    """Busca um cliente pelo ID"""
    cliente = await repository.get_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return {
        "status": "success",
        "cliente": cliente.dict()
    }

@router.get("/")
async def listar_clientes(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    repository: ClienteRepository = Depends(get_cliente_repository)
):
    """Lista todos os clientes com paginação"""
    clientes = await repository.list_all(skip=skip, limit=limit)
    total = await repository.count()
    
    return {
        "status": "success",
        "clientes": clientes,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_more": skip + limit < total
        }
    }

@router.get("/search/nome")
async def buscar_por_nome(
    nome: str = Query(..., description="Nome para buscar"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: ClienteRepository = Depends(get_cliente_repository)
):
    """Busca clientes por nome (busca parcial)"""
    clientes = await repository.search_by_name(nome, skip=skip, limit=limit)
    
    return {
        "status": "success",
        "clientes": clientes,
        "search_term": nome
    }

@router.put("/{cliente_id}")
async def atualizar_cliente(
    cliente_id: str,
    cliente: Cliente,
    repository: ClienteRepository = Depends(get_cliente_repository)
):
    """Atualiza um cliente existente"""
    # Verifica se o cliente existe
    existing_cliente = await repository.get_by_id(cliente_id)
    if not existing_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Atualiza o cliente
    success = await repository.update(cliente_id, cliente)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao atualizar cliente")
    
    return {
        "status": "success",
        "message": "Cliente atualizado com sucesso",
        "cliente_id": cliente_id
    }

@router.delete("/{cliente_id}")
async def deletar_cliente(
    cliente_id: str,
    repository: ClienteRepository = Depends(get_cliente_repository)
):
    """Remove um cliente"""
    # Verifica se o cliente existe
    existing_cliente = await repository.get_by_id(cliente_id)
    if not existing_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Remove o cliente
    success = await repository.delete(cliente_id)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao deletar cliente")
    
    return {
        "status": "success",
        "message": "Cliente removido com sucesso"
    }