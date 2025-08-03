from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from ..forms import AgendamentoForm
from ..models import Agendamento, HistoricoAgendamento, Profissional
from ..utils import get_local_today


class AgendamentoListView(ListView):
    """Lista de agendamentos com filtros"""

    model = Agendamento
    template_name = "appointments/agendamento_list.html"
    context_object_name = "agendamentos"
    paginate_by = 20

    def get_queryset(self):
        queryset = Agendamento.objects.select_related(
            "cliente", "profissional", "servico"
        ).order_by("-data_hora")

        # Filtros
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        profissional = self.request.GET.get("profissional")
        if profissional:
            queryset = queryset.filter(profissional_id=profissional)

        data_inicio = self.request.GET.get("data_inicio")
        if data_inicio:
            queryset = queryset.filter(data_hora__date__gte=data_inicio)

        data_fim = self.request.GET.get("data_fim")
        if data_fim:
            queryset = queryset.filter(data_hora__date__lte=data_fim)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profissionais"] = Profissional.objects.filter(ativo=True)
        context["status_choices"] = Agendamento.STATUS_CHOICES
        return context


class AgendamentoDetailView(DetailView):
    """Detalhes do agendamento"""

    model = Agendamento
    template_name = "appointments/agendamento_detail.html"
    context_object_name = "agendamento"

    def get_queryset(self):
        return Agendamento.objects.select_related("cliente", "profissional", "servico")


class AgendamentoCreateView(CreateView):
    """Criação de novo agendamento"""

    model = Agendamento
    form_class = AgendamentoForm
    template_name = "appointments/agendamento_form.html"
    success_url = reverse_lazy("appointments:agendamento_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            # Criar histórico de criação
            HistoricoAgendamento.objects.create(
                agendamento=self.object,
                tipo_acao="CRIADO",
                descricao=f"Agendamento criado para {self.object.cliente.nome} com {self.object.profissional.nome}",
                status_novo=self.object.status,
                usuario="Sistema",
            )

            return response

        except IntegrityError:
            # Tratar conflito de horário de forma elegante
            form.add_error(
                None,
                "Este horário já foi ocupado por outro agendamento. "
                "Por favor, selecione um horário diferente.",
            )
            return self.form_invalid(form)

        messages.success(self.request, "Agendamento criado com sucesso!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Novo Agendamento"
        context["botao_texto"] = "Criar Agendamento"
        return context


class AgendamentoUpdateView(UpdateView):
    """Edição de agendamento"""

    model = Agendamento
    form_class = AgendamentoForm
    template_name = "appointments/agendamento_form.html"
    success_url = reverse_lazy("appointments:agendamento_list")

    def get_queryset(self):
        return Agendamento.objects.select_related("cliente", "profissional", "servico")

    def form_valid(self, form):
        messages.success(self.request, "Agendamento atualizado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar Agendamento"
        context["botao_texto"] = "Salvar Alterações"
        return context


def atualizar_status_agendamento(request, pk):
    """Atualizar status do agendamento via AJAX"""
    if request.method == "POST":
        agendamento = get_object_or_404(Agendamento, pk=pk)
        novo_status = request.POST.get("status")

        # Validação: não permitir "EM_ANDAMENTO" para datas passadas
        if (
            novo_status == "EM_ANDAMENTO"
            and agendamento.data_hora.date() < get_local_today()
        ):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "error": 'Não é possível marcar como "Em Andamento" agendamentos de datas passadas',
                    }
                )
            else:
                messages.error(
                    request,
                    'Não é possível marcar como "Em Andamento" agendamentos de datas passadas',
                )
                return redirect("appointments:agendamento_detail", pk=pk)

        if novo_status in dict(Agendamento.STATUS_CHOICES):
            status_anterior = agendamento.status
            agendamento.status = novo_status
            agendamento.save()

            # Criar histórico da mudança de status
            descricoes = {
                "AGENDADO": "Agendamento confirmado e agendado",
                "CONFIRMADO": "Cliente confirmou o agendamento",
                "EM_ANDAMENTO": "Atendimento iniciado",
                "CONCLUIDO": "Atendimento finalizado com sucesso",
                "CANCELADO": "Agendamento foi cancelado",
                "NAO_COMPARECEU": "Cliente não compareceu ao agendamento",
            }

            HistoricoAgendamento.objects.create(
                agendamento=agendamento,
                tipo_acao="STATUS_ALTERADO",
                descricao=descricoes.get(
                    novo_status,
                    f"Status alterado para {agendamento.get_status_display()}",
                ),
                status_anterior=status_anterior,
                status_novo=novo_status,
                usuario="Sistema",
            )

            messages.success(
                request, f"Status atualizado para {agendamento.get_status_display()}"
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Status atualizado para {agendamento.get_status_display()}",
                    }
                )
        else:
            messages.error(request, "Status inválido")

    return redirect("appointments:agendamento_detail", pk=pk)
