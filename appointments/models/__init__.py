# Imports centralizados para manter compatibilidade
from .agendamento import Agendamento
from .cliente import Cliente
from .historico import HistoricoAgendamento
from .profissional import Profissional
from .servico import Servico

__all__ = [
    "Cliente",
    "Servico",
    "Profissional",
    "Agendamento",
    "HistoricoAgendamento",
]
