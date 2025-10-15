from enum import Enum

class ClassificacaoLead(str, Enum):
    """Enum para representar a classificação de um lead."""
    LEAD_FRIO = "Demonstrou pouco interesse, sabe pouco sobre sua solução."
    LEAD_MORNO = "Mostrou interesse, mas ainda está em fase de aprendizado."
    LEAD_QUENTE = "Pronto para ser abordado por vendas."

    @classmethod
    def get_default(cls):
        return cls.LEAD_FRIO
