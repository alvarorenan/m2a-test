from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Agendamentos
    path("agendamentos/", views.AgendamentoListView.as_view(), name="agendamento_list"),
    path(
        "agendamentos/<int:pk>/",
        views.AgendamentoDetailView.as_view(),
        name="agendamento_detail",
    ),
    path(
        "agendamentos/novo/",
        views.AgendamentoCreateView.as_view(),
        name="agendamento_create",
    ),
    path(
        "agendamentos/<int:pk>/editar/",
        views.AgendamentoUpdateView.as_view(),
        name="agendamento_edit",
    ),
    path(
        "agendamentos/<int:pk>/status/",
        views.atualizar_status_agendamento,
        name="atualizar_status",
    ),
    # Relatórios
    path("relatorios/servicos/", views.relatorio_servicos, name="relatorio_servicos"),
    # Clientes
    path("clientes/", views.ClienteListView.as_view(), name="cliente_list"),
    path("clientes/novo/", views.ClienteCreateView.as_view(), name="cliente_create"),
    path(
        "clientes/<int:pk>/editar/",
        views.ClienteUpdateView.as_view(),
        name="cliente_update",
    ),
    # Profissionais
    path(
        "profissionais/", views.ProfissionalListView.as_view(), name="profissional_list"
    ),
    path(
        "profissionais/novo/",
        views.ProfissionalCreateView.as_view(),
        name="profissional_create",
    ),
    path(
        "profissionais/<int:pk>/editar/",
        views.ProfissionalUpdateView.as_view(),
        name="profissional_update",
    ),
    # Serviços
    path("servicos/", views.ServicoListView.as_view(), name="servico_list"),
    path("servicos/novo/", views.ServicoCreateView.as_view(), name="servico_create"),
    path(
        "servicos/<int:pk>/editar/",
        views.ServicoUpdateView.as_view(),
        name="servico_update",
    ),
    # APIs
    path(
        "api/horarios-disponiveis/",
        views.api_horarios_disponiveis,
        name="api_horarios_disponiveis",
    ),
]
