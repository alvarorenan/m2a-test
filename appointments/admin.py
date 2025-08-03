from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Agendamento, Cliente, Profissional, Servico


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "telefone",
        "email",
        "ativo",
        "total_agendamentos",
        "data_cadastro",
    ]
    list_filter = ["ativo", "data_cadastro", "data_nascimento"]
    search_fields = ["nome", "telefone", "email"]
    list_editable = ["ativo"]
    readonly_fields = ["data_cadastro", "data_atualizacao"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("nome", "telefone", "email")}),
        (
            "Informações Complementares",
            {"fields": ("endereco", "data_nascimento", "observacoes")},
        ),
        ("Status", {"fields": ("ativo",)}),
        (
            "Auditoria",
            {"fields": ("data_cadastro", "data_atualizacao"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(total_agendamentos=Count("agendamento"))
        )

    def total_agendamentos(self, obj):
        return obj.total_agendamentos

    total_agendamentos.short_description = "Total de Agendamentos"
    total_agendamentos.admin_order_field = "total_agendamentos"


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "categoria",
        "preco_formatado",
        "duracao_formatada",
        "ativo",
        "total_agendamentos",
    ]
    list_filter = ["categoria", "ativo", "data_cadastro"]
    search_fields = ["nome", "descricao"]
    list_editable = ["ativo"]
    readonly_fields = ["data_cadastro", "data_atualizacao"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("nome", "categoria", "descricao")}),
        ("Preço e Duração", {"fields": ("preco", "duracao_minutos")}),
        ("Status", {"fields": ("ativo",)}),
        (
            "Auditoria",
            {"fields": ("data_cadastro", "data_atualizacao"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(total_agendamentos=Count("agendamento"))
        )

    def preco_formatado(self, obj):
        return f"R$ {obj.preco:.2f}"

    preco_formatado.short_description = "Preço"
    preco_formatado.admin_order_field = "preco"

    def duracao_formatada(self, obj):
        horas = obj.duracao_minutos // 60
        minutos = obj.duracao_minutos % 60
        if horas:
            return f"{horas}h {minutos}min"
        return f"{minutos}min"

    duracao_formatada.short_description = "Duração"
    duracao_formatada.admin_order_field = "duracao_minutos"

    def total_agendamentos(self, obj):
        return obj.total_agendamentos

    total_agendamentos.short_description = "Total de Agendamentos"
    total_agendamentos.admin_order_field = "total_agendamentos"


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "telefone",
        "horario_trabalho",
        "ativo",
        "total_agendamentos",
    ]
    list_filter = ["ativo", "data_cadastro", "especialidades"]
    search_fields = ["nome", "telefone", "email"]
    list_editable = ["ativo"]
    readonly_fields = ["data_cadastro", "data_atualizacao"]
    filter_horizontal = ["especialidades"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("nome", "telefone", "email")}),
        (
            "Horário de Trabalho",
            {"fields": ("horario_inicio", "horario_fim", "dias_semana")},
        ),
        ("Especialidades", {"fields": ("especialidades",)}),
        ("Status", {"fields": ("ativo",)}),
        (
            "Auditoria",
            {"fields": ("data_cadastro", "data_atualizacao"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(total_agendamentos=Count("agendamento"))
        )

    def horario_trabalho(self, obj):
        return f"{obj.horario_inicio} - {obj.horario_fim}"

    horario_trabalho.short_description = "Horário"

    def total_agendamentos(self, obj):
        return obj.total_agendamentos

    total_agendamentos.short_description = "Total de Agendamentos"
    total_agendamentos.admin_order_field = "total_agendamentos"


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = [
        "cliente",
        "profissional",
        "servico",
        "data_hora_formatada",
        "status_colorido",
        "preco_final_formatado",
    ]
    list_filter = [
        "status",
        "data_hora",
        "profissional",
        "servico__categoria",
        "data_cadastro",
    ]
    search_fields = [
        "cliente__nome",
        "profissional__nome",
        "servico__nome",
        "observacoes",
    ]
    # list_editable = ['status']  # Removido porque usamos status_colorido na display
    readonly_fields = ["data_cadastro", "data_atualizacao", "data_hora_fim_calculada"]
    date_hierarchy = "data_hora"

    fieldsets = (
        (
            "Agendamento",
            {"fields": ("cliente", "profissional", "servico", "data_hora")},
        ),
        ("Detalhes", {"fields": ("status", "preco_final", "observacoes")}),
        (
            "Informações Calculadas",
            {"fields": ("data_hora_fim_calculada",), "classes": ("collapse",)},
        ),
        (
            "Auditoria",
            {"fields": ("data_cadastro", "data_atualizacao"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("cliente", "profissional", "servico")
        )

    def data_hora_formatada(self, obj):
        return obj.data_hora.strftime("%d/%m/%Y %H:%M")

    data_hora_formatada.short_description = "Data e Hora"
    data_hora_formatada.admin_order_field = "data_hora"

    def status_colorido(self, obj):
        colors = {
            "AGENDADO": "blue",
            "CONFIRMADO": "green",
            "EM_ANDAMENTO": "orange",
            "CONCLUIDO": "darkgreen",
            "CANCELADO": "red",
            "NAO_COMPARECEU": "darkred",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colorido.short_description = "Status"
    status_colorido.admin_order_field = "status"

    def preco_final_formatado(self, obj):
        return f"R$ {obj.preco_final:.2f}" if obj.preco_final else "-"

    preco_final_formatado.short_description = "Preço Final"
    preco_final_formatado.admin_order_field = "preco_final"

    def data_hora_fim_calculada(self, obj):
        return obj.data_hora_fim.strftime("%d/%m/%Y %H:%M")

    data_hora_fim_calculada.short_description = "Data/Hora de Fim (Calculada)"

    # Ações personalizadas
    actions = [
        "marcar_como_confirmado",
        "marcar_como_concluido",
        "marcar_como_cancelado",
    ]

    def marcar_como_confirmado(self, request, queryset):
        updated = queryset.filter(status="AGENDADO").update(status="CONFIRMADO")
        self.message_user(
            request, f"{updated} agendamento(s) marcado(s) como confirmado(s)."
        )

    marcar_como_confirmado.short_description = "Marcar selecionados como confirmados"

    def marcar_como_concluido(self, request, queryset):
        updated = queryset.filter(status__in=["CONFIRMADO", "EM_ANDAMENTO"]).update(
            status="CONCLUIDO"
        )
        self.message_user(
            request, f"{updated} agendamento(s) marcado(s) como concluído(s)."
        )

    marcar_como_concluido.short_description = "Marcar selecionados como concluídos"

    def marcar_como_cancelado(self, request, queryset):
        updated = queryset.filter(status__in=["AGENDADO", "CONFIRMADO"]).update(
            status="CANCELADO"
        )
        self.message_user(request, f"{updated} agendamento(s) cancelado(s).")

    marcar_como_cancelado.short_description = "Cancelar selecionados"


# Customização do site admin
admin.site.site_header = "Sistema de Agendamento - Salão de Beleza"
admin.site.site_title = "Salão Admin"
admin.site.index_title = "Painel Administrativo"
