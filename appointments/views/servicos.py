from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import ServicoForm
from ..models import Servico


class ServicoListView(ListView):
    model = Servico
    template_name = "appointments/servicos/servico_list.html"
    context_object_name = "servicos"
    paginate_by = 20

    def get_queryset(self):
        queryset = Servico.objects.filter(ativo=True)
        categoria = self.request.GET.get("categoria", "")
        search = self.request.GET.get("search", "")

        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if search:
            queryset = queryset.filter(nome__icontains=search)

        return queryset.order_by("categoria", "nome")


class ServicoCreateView(CreateView):
    model = Servico
    form_class = ServicoForm
    template_name = "appointments/servicos/servico_form.html"
    success_url = reverse_lazy("appointments:servico_list")

    def form_valid(self, form):
        messages.success(self.request, "Serviço cadastrado com sucesso!")
        return super().form_valid(form)


class ServicoUpdateView(UpdateView):
    model = Servico
    form_class = ServicoForm
    template_name = "appointments/servicos/servico_form.html"
    success_url = reverse_lazy("appointments:servico_list")

    def form_valid(self, form):
        messages.success(self.request, "Serviço atualizado com sucesso!")
        return super().form_valid(form)
