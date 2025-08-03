from datetime import datetime, timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from ..models import Agendamento


class RelatorioService:
    """Service para geração de relatórios"""

    @staticmethod
    def relatorio_servicos_concluidos(
        data_inicio=None, data_fim=None, profissional_id=None
    ):
        """Gerar relatório de serviços concluídos"""

        # Data padrão: último mês
        if not data_inicio:
            data_inicio = (timezone.now() - timedelta(days=30)).date()
        elif isinstance(data_inicio, str):
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()

        if not data_fim:
            data_fim = timezone.now().date()
        elif isinstance(data_fim, str):
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

        # Query base
        queryset = Agendamento.objects.filter(
            status="CONCLUIDO",
            data_hora__date__gte=data_inicio,
            data_hora__date__lte=data_fim,
        ).select_related("servico", "profissional", "cliente")

        if profissional_id:
            queryset = queryset.filter(profissional_id=profissional_id)

        # Estatísticas por serviço
        servicos_stats = (
            queryset.values("servico__nome", "servico__categoria")
            .annotate(total_servicos=Count("id"), receita_total=Sum("preco_final"))
            .order_by("-total_servicos")
        )

        # Estatísticas por profissional
        profissionais_stats = (
            queryset.values("profissional__nome")
            .annotate(total_servicos=Count("id"), receita_total=Sum("preco_final"))
            .order_by("-total_servicos")
        )

        # Estatísticas gerais
        stats_gerais = queryset.aggregate(
            total_agendamentos=Count("id"),
            receita_total=Sum("preco_final"),
        )

        # Calcular ticket médio
        if stats_gerais["total_agendamentos"] > 0:
            stats_gerais["ticket_medio"] = (
                stats_gerais["receita_total"] / stats_gerais["total_agendamentos"]
            )
        else:
            stats_gerais["ticket_medio"] = 0

        # Evolução diária
        agendamentos_por_dia = (
            queryset.extra(select={"data": "DATE(data_hora)"})
            .values("data")
            .annotate(total=Count("id"), receita=Sum("preco_final"))
            .order_by("data")
        )

        return {
            "servicos_stats": servicos_stats,
            "profissionais_stats": profissionais_stats,
            "stats_gerais": stats_gerais,
            "agendamentos_por_dia": list(agendamentos_por_dia),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "periodo_dias": (data_fim - data_inicio).days + 1,
        }

    @staticmethod
    def dashboard_stats(data=None):
        """Estatísticas para o dashboard"""

        if not data:
            data = timezone.now().date()

        # Agendamentos do dia
        agendamentos_dia = Agendamento.objects.filter(
            data_hora__date=data
        ).select_related("cliente", "profissional", "servico")

        # Estatísticas básicas
        stats = {
            "agendamentos_hoje": agendamentos_dia.count(),
            "agendamentos_confirmados": agendamentos_dia.filter(
                status="CONFIRMADO"
            ).count(),
            "agendamentos_concluidos": agendamentos_dia.filter(
                status="CONCLUIDO"
            ).count(),
            "agendamentos_cancelados": agendamentos_dia.filter(
                status="CANCELADO"
            ).count(),
        }

        # Próximos agendamentos
        proximos_agendamentos = (
            Agendamento.objects.filter(
                data_hora__gte=timezone.now(), status__in=["AGENDADO", "CONFIRMADO"]
            )
            .select_related("cliente", "profissional", "servico")
            .order_by("data_hora")[:5]
        )

        return {
            "stats": stats,
            "agendamentos_hoje": agendamentos_dia.order_by("data_hora"),
            "proximos_agendamentos": proximos_agendamentos,
        }

    @staticmethod
    def relatorio_profissional(profissional_id, periodo_dias=30):
        """Relatório específico de um profissional"""

        data_inicio = timezone.now().date() - timedelta(days=periodo_dias)
        data_fim = timezone.now().date()

        agendamentos = Agendamento.objects.filter(
            profissional_id=profissional_id,
            data_hora__date__gte=data_inicio,
            data_hora__date__lte=data_fim,
        ).select_related("servico", "cliente")

        # Estatísticas
        total_agendamentos = agendamentos.count()
        concluidos = agendamentos.filter(status="CONCLUIDO")
        cancelados = agendamentos.filter(status="CANCELADO")

        receita_total = concluidos.aggregate(total=Sum("preco_final"))["total"] or 0

        # Serviços mais realizados
        servicos_realizados = (
            concluidos.values("servico__nome")
            .annotate(quantidade=Count("id"))
            .order_by("-quantidade")[:5]
        )

        return {
            "total_agendamentos": total_agendamentos,
            "total_concluidos": concluidos.count(),
            "total_cancelados": cancelados.count(),
            "receita_total": receita_total,
            "servicos_realizados": servicos_realizados,
            "taxa_conclusao": (
                (concluidos.count() / total_agendamentos * 100)
                if total_agendamentos > 0
                else 0
            ),
        }
