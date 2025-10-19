from __future__ import annotations
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
import unicodedata
from .endereco import Endereco
from .origem import OrigemLead
from .classificacao import ClassificacaoLead

class Cliente(BaseModel):
    """Modelo para representar um cliente"""
    nome: str = Field(..., description="Nome completo do cliente")
    telefone: List[str] = Field(default_factory=list, description="Lista de telefones do cliente")
    email: List[str] = Field(default_factory=list, description="Lista de emails do cliente")
    nascimento: str = Field(..., description="Data de nascimento (formato: YYYY-MM-DD)")
    origem: OrigemLead = Field(default=OrigemLead.get_default(), description="Origem do cliente (ex: website, indicação, etc.)")
    classificacao: ClassificacaoLead = Field(default=ClassificacaoLead.get_default(), description="Classificação do lead (frio, morno, quente)")
    enderecos: List[Endereco] = Field(default_factory=list, description="Lista de endereços do cliente")

    @staticmethod
    def _normalize_text(value: str) -> str:
        """Normaliza texto para comparação: remove acentos, baixa caixa e remove espaços/pontuação."""
        nfkd = unicodedata.normalize("NFKD", value)
        no_accents = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
        lowered = no_accents.lower()
        # remove caracteres não alfanuméricos
        return "".join(ch for ch in lowered if ch.isalnum())

    @validator("origem", pre=True)
    def validate_origem(cls, v: Union[str, OrigemLead, None]):
        if v is None or v == "":
            return OrigemLead.get_default()
        if isinstance(v, OrigemLead):
            return v
        if isinstance(v, str):
            key = cls._normalize_text(v)
            mapping = {
                # Preencheu Formulário
                "preencheuformulario": OrigemLead.PREENCHEU_FORMULARIO,
                "formulario": OrigemLead.PREENCHEU_FORMULARIO,
                "formulario": OrigemLead.PREENCHEU_FORMULARIO,
                "form": OrigemLead.PREENCHEU_FORMULARIO,
                # Indicação
                "indicacao": OrigemLead.INDICACAO,
                "indicacao": OrigemLead.INDICACAO,
                "indic": OrigemLead.INDICACAO,
                # Website
                "website": OrigemLead.WEBSITE,
                "site": OrigemLead.WEBSITE,
                "web": OrigemLead.WEBSITE,
                # Rede Social
                "redesocial": OrigemLead.REDE_SOCIAL,
                "instagram": OrigemLead.REDE_SOCIAL,
                "facebook": OrigemLead.REDE_SOCIAL,
                "tiktok": OrigemLead.REDE_SOCIAL,
                # Clicou em Anúncio
                "clicouemanuncio": OrigemLead.CLICOU_ANUNCIO,
                "anuncio": OrigemLead.CLICOU_ANUNCIO,
                "ads": OrigemLead.CLICOU_ANUNCIO,
                # Campanha de Email
                "campanhadeemail": OrigemLead.CAMPANHA_EMAIL,
                "email": OrigemLead.CAMPANHA_EMAIL,
                "mailing": OrigemLead.CAMPANHA_EMAIL,
                # Eventos Profissionais
                "eventosprofissionais": OrigemLead.EVENTOS_PROFISSIONAIS,
                "evento": OrigemLead.EVENTOS_PROFISSIONAIS,
                "feira": OrigemLead.EVENTOS_PROFISSIONAIS,
                # Parcerias
                "parcerias": OrigemLead.PARCERIAS,
                "parceria": OrigemLead.PARCERIAS,
                "parceiro": OrigemLead.PARCERIAS,
                # Outra Origem
                "outraorigem": OrigemLead.OUTRA_ORIGEM,
                "outra": OrigemLead.OUTRA_ORIGEM,
                "outro": OrigemLead.OUTRA_ORIGEM,
                "outros": OrigemLead.OUTRA_ORIGEM,
            }
            if key in mapping:
                return mapping[key]
            # fallback: tenta corresponder exatamente algum valor do Enum sem normalizar
            for item in OrigemLead:
                if v == item.value:
                    return item
            # último recurso: manter padrão
            return OrigemLead.get_default()
        # tipos inesperados delegam para Pydantic (vai falhar com 422 se inaceitável)
        return v

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
                "classificacao": "morno",
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
