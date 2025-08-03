# Imports centralizados para manter compatibilidade
from .agendamentos import *
from .api import *
from .clientes import *
from .dashboard import dashboard
from .profissionais import *
from .relatorios import *
from .servicos import *

__all__ = [
    "dashboard",
    # Agendamentos
    "AgendamentoListView",
    "AgendamentoDetailView",
    "AgendamentoCreateView",
    "AgendamentoUpdateView",
    "atualizar_status_agendamento",
    # Clientes
    "ClienteListView",
    "ClienteCreateView",
    "ClienteUpdateView",
    # Profissionais
    "ProfissionalListView",
    "ProfissionalCreateView",
    "ProfissionalUpdateView",
    # Serviços
    "ServicoListView",
    "ServicoCreateView",
    "ServicoUpdateView",
    # Relatórios
    "relatorio_servicos",
    # API
    "api_horarios_disponiveis",
]
