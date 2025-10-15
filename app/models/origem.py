from enum import Enum

class OrigemLead(str, Enum):
    """Enum para representar a origem de um lead."""
    PREENCHEU_FORMULARIO = "PREENCHEU_FORMULARIO"
    CLICOU_ANUNCIO = "CLICOU_ANUNCIO"
    BAIXOU_MATERIAL = "BAIXOU_MATERIAL"

    @classmethod
    def get_default(cls):
        return cls.PREENCHEU_FORMULARIO
