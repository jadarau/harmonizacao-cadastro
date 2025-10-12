from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, validator

class Endereco(BaseModel):
    """Modelo para representar um endereço do cliente"""
    logradouro: str = Field(..., description="Nome da rua, avenida, etc.")
    numero: Optional[str] = Field(None, description="Número do imóvel")
    complemento: Optional[str] = Field(None, description="Complemento do endereço")
    bairro: str = Field(..., description="Nome do bairro")
    cidade: str = Field(..., description="Nome da cidade")
    estado: str = Field(..., description="Estado ou UF")
    cep: str = Field(..., description="CEP do endereço")
    tipo: Optional[str] = Field("residencial", description="Tipo do endereço (residencial, comercial, etc.)")

    @validator("cep")
    def validate_cep(cls, v: str):
        # Remove caracteres não numéricos
        cep_clean = ''.join(filter(str.isdigit, v))
        if len(cep_clean) != 8:
            raise ValueError("CEP deve conter 8 dígitos")
        return cep_clean

    class Config:
        json_schema_extra = {
            "example": {
                "logradouro": "Rua das Flores",
                "numero": "123",
                "complemento": "Apt 45",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234567",
                "tipo": "residencial"
            }
        }