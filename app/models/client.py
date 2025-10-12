from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .endereco import Endereco

class Cliente(BaseModel):
    """Modelo para representar um cliente"""
    nome: str = Field(..., description="Nome completo do cliente")
    telefone: List[str] = Field(default_factory=list, description="Lista de telefones do cliente")
    email: List[str] = Field(default_factory=list, description="Lista de emails do cliente")
    nascimento: str = Field(..., description="Data de nascimento (formato: YYYY-MM-DD)")
    origem: Optional[str] = Field(None, description="Origem do cliente (ex: website, indicação, etc.)")
    enderecos: List[Endereco] = Field(default_factory=list, description="Lista de endereços do cliente")

    @validator("telefone")
    def validate_telefone(cls, v: List[str]):
        if not v:
            return v
        
        telefones_validos = []
        for tel in v:
            # Remove caracteres não numéricos
            tel_clean = ''.join(filter(str.isdigit, tel))
            if len(tel_clean) < 10 or len(tel_clean) > 11:
                raise ValueError(f"Telefone inválido: {tel}. Deve conter 10 ou 11 dígitos")
            telefones_validos.append(tel_clean)
        
        return telefones_validos

    @validator("email")
    def validate_email(cls, v: List[str]):
        if not v:
            return v
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in v:
            if not re.match(email_pattern, email):
                raise ValueError(f"Email inválido: {email}")
        
        return v

    @validator("nascimento")
    def validate_nascimento(cls, v: str):
        try:
            # Valida se a data está no formato correto
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Data de nascimento deve estar no formato YYYY-MM-DD")

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva Santos",
                "telefone": ["11987654321", "1133334444"],
                "email": ["joao@email.com", "joao.silva@empresa.com"],
                "nascimento": "1990-05-15",
                "origem": "website",
                "enderecos": [
                    {
                        "logradouro": "Rua das Flores",
                        "numero": "123",
                        "complemento": "Apt 45",
                        "bairro": "Centro",
                        "cidade": "São Paulo",
                        "estado": "SP",
                        "cep": "01234567",
                        "tipo": "residencial"
                    }
                ]
            }
        }
