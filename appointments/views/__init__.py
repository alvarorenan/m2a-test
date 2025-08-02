# Imports centralizados para manter compatibilidade
from .dashboard import dashboard
from .agendamentos import *
from .clientes import *
from .profissionais import *
from .servicos import *
from .relatorios import *
from .api import *

__all__ = [
    'dashboard',
    # Agendamentos
    'AgendamentoListView', 'AgendamentoDetailView', 'AgendamentoCreateView', 
    'AgendamentoUpdateView', 'atualizar_status_agendamento',
    # Clientes
    'ClienteListView', 'ClienteCreateView', 'ClienteUpdateView',
    # Profissionais
    'ProfissionalListView', 'ProfissionalCreateView', 'ProfissionalUpdateView',
    # Serviços
    'ServicoListView', 'ServicoCreateView', 'ServicoUpdateView',
    # Relatórios
    'relatorio_servicos',
    # API
    'api_horarios_disponiveis',
]