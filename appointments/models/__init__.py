# Imports centralizados para manter compatibilidade
from .cliente import Cliente
from .servico import Servico
from .profissional import Profissional
from .agendamento import Agendamento
from .historico import HistoricoAgendamento

__all__ = [
    'Cliente',
    'Servico', 
    'Profissional',
    'Agendamento',
    'HistoricoAgendamento',
]