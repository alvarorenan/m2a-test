from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy

from ..models import Cliente
from ..forms import ClienteForm


class ClienteListView(ListView):
    model = Cliente
    template_name = 'appointments/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        queryset = Cliente.objects.filter(ativo=True)
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(telefone__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset.order_by('nome')


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'appointments/cliente_form.html'
    success_url = reverse_lazy('appointments:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente cadastrado com sucesso!')
        return super().form_valid(form)


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'appointments/cliente_form.html'
    success_url = reverse_lazy('appointments:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)