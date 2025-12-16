from __future__ import annotations
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Cliente
from app.database.deps import get_cliente_repository
from app.database.repository import ClienteRepository
from app.services.rag_service import RAGService
from app.models.endereco import Endereco
from typing import Optional
from app.services.kafka_producer import send_cliente_event

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
        # Classifica o cliente usando o RAG antes de salvar/atualizar
        classificacao = rag_service.classificar_cliente(cliente.dict())
        incoming = cliente.dict()
        incoming["classificacao_rag"] = classificacao

        # Busca cliente apenas por email (telefone/endereço não bloqueiam criação)
        existing: Optional[Cliente] = None
        for e in (incoming.get("email", []) or []):
            found = await repository.get_by_email(e)
            if found:
                existing = found
                break

        created = False
        cliente_id: Optional[str] = None

        if not existing:
            # Não existe: criar novo
            cliente_id = await repository.create(Cliente(**incoming))
            created = True
        else:
            # Existe: unificar emails/telefones e endereços
            # recuperar id bruto via listagem rápida para o email
            # como get_by_email retorna modelo, precisamos achar o documento
            raw = await repository.find_by_email_or_phone(
                emails=incoming.get("email", []),
                telefones=[]
            )
            cliente_id = raw["id"] if raw else None

            # Normaliza conjuntos para evitar duplicatas
            existing_emails = set(existing.get("email", []) or [])
            existing_tels = set(existing.get("telefone", []) or [])

            new_emails = [e for e in incoming.get("email", []) if e not in existing_emails]
            new_tels = [t for t in incoming.get("telefone", []) if t not in existing_tels]

            # Endereços: adicionar se não existir nenhum igual (comparação por campos principais)
            enderecos_to_add = []
            incoming_enderecos = incoming.get("enderecos", []) or []
            existing_enderecos = existing.get("enderecos", []) or []

            def endereco_key(e: dict) -> tuple:
                return (
                    e.get("logradouro"), e.get("numero"), e.get("complemento"),
                    e.get("bairro"), e.get("cidade"), e.get("estado"), e.get("cep"), e.get("tipo")
                )

            existing_keys = {endereco_key(e) for e in existing_enderecos}
            for e in incoming_enderecos:
                if endereco_key(e) not in existing_keys:
                    # valida via modelo Endereco
                    enderecos_to_add.append(Endereco(**e).dict())

            # Atualiza apenas se houver algo novo
            await repository.update_add_fields(
                cliente_id=cliente_id,
                emails_to_add=new_emails or None,
                telefones_to_add=new_tels or None,
                enderecos_to_add=enderecos_to_add or None,
                extra_set={"classificacao_rag": classificacao}
            )

        # Monta resposta/objeto do cliente resultante
        # Se criamos, usamos incoming; se atualizamos, refazemos merge localmente para retornar
        if created:
            result_cliente = {**incoming}
        else:
            # merge: existentes + novos
            result_cliente = {**existing.dict()}
            result_cliente.pop("id", None)
            result_cliente["email"] = sorted(list(set(existing.get("email", []) or []) | set(incoming.get("email", []) or [])))
            result_cliente["telefone"] = sorted(list(set(existing.get("telefone", []) or []) | set(incoming.get("telefone", []) or [])))
            # endereços
            merged_enderecos = existing.get("enderecos", []) or []
            if incoming.get("enderecos"):
                # adiciona aqueles que não estavam
                ex_keys = {(
                    e.get("logradouro"), e.get("numero"), e.get("complemento"),
                    e.get("bairro"), e.get("cidade"), e.get("estado"), e.get("cep"), e.get("tipo")
                ) for e in merged_enderecos}
                for e in incoming["enderecos"]:
                    key = (
                        e.get("logradouro"), e.get("numero"), e.get("complemento"),
                        e.get("bairro"), e.get("cidade"), e.get("estado"), e.get("cep"), e.get("tipo")
                    )
                    if key not in ex_keys:
                        merged_enderecos.append(e)
                        ex_keys.add(key)
            result_cliente["enderecos"] = merged_enderecos
            result_cliente["classificacao_rag"] = classificacao

        # Envia evento para Kafka (se habilitado)
        try:
            await send_cliente_event({
                "event": "cliente_created" if created else "cliente_updated",
                "cliente_id": cliente_id,
                "cliente": result_cliente,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            # Não falha a requisição por erro de mensageria
            pass

        return {
            "status": "success",
            "message": "Cliente criado com sucesso" if created else "Cliente atualizado com sucesso",
            "cliente_id": cliente_id,
            "cliente": result_cliente,
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