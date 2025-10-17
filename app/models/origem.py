from enum import Enum

class OrigemLead(str, Enum):
    """Enum para representar a origem de um lead."""
    PREENCHEU_FORMULARIO = "Preencheu Formulário"
    INDICACAO = "Indicação"
    WEBSITE = "Website"
    REDE_SOCIAL = "Rede Social"
    CLICOU_ANUNCIO = "Clicou em Anúncio"
    CAMPANHA_EMAIL = "Campanha de Email"
    EVENTOS_PROFISSIONAIS = "Eventos Profissionais"
    PARCERIAS = "Parcerias"
    OUTRA_ORIGEM = "Outra Origem"

    @classmethod
    def get_default(cls):
        return cls.PREENCHEU_FORMULARIO
