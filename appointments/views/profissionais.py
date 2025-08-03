from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import ProfissionalForm
from ..models import Profissional


class ProfissionalListView(ListView):
    model = Profissional
    template_name = "appointments/profissional_list.html"
    context_object_name = "profissionais"
    paginate_by = 20

    def get_queryset(self):
        queryset = Profissional.objects.filter(ativo=True).prefetch_related(
            "especialidades"
        )
        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | Q(email__icontains=search)
            )
        return queryset.order_by("nome")


class ProfissionalCreateView(CreateView):
    model = Profissional
    form_class = ProfissionalForm
    template_name = "appointments/profissional_form.html"
    success_url = reverse_lazy("appointments:profissional_list")

    def form_valid(self, form):
        messages.success(self.request, "Profissional cadastrado com sucesso!")
        return super().form_valid(form)


class ProfissionalUpdateView(UpdateView):
    model = Profissional
    form_class = ProfissionalForm
    template_name = "appointments/profissional_form.html"
    success_url = reverse_lazy("appointments:profissional_list")

    def form_valid(self, form):
        messages.success(self.request, "Profissional atualizado com sucesso!")
        return super().form_valid(form)
