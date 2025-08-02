from django.shortcuts import render
from django.utils import timezone
from ..models import Cliente, Servico, Profissional, Agendamento


def dashboard(request):
    """Dashboard principal do sistema"""
    hoje = timezone.now().date()
    
    # Estatísticas do dia
    agendamentos_hoje = Agendamento.objects.filter(
        data_hora__date=hoje
    ).select_related('cliente', 'profissional', 'servico')
    
    stats = {
        'agendamentos_hoje': agendamentos_hoje.count(),
        'agendamentos_confirmados': agendamentos_hoje.filter(status='CONFIRMADO').count(),
        'agendamentos_concluidos': agendamentos_hoje.filter(status='CONCLUIDO').count(),
        'agendamentos_cancelados': agendamentos_hoje.filter(status='CANCELADO').count(),
        'total_clientes': Cliente.objects.filter(ativo=True).count(),
        'total_profissionais': Profissional.objects.filter(ativo=True).count(),
        'total_servicos': Servico.objects.filter(ativo=True).count(),
    }
    
    # Próximos agendamentos
    proximos_agendamentos = Agendamento.objects.filter(
        data_hora__gte=timezone.now(),
        status__in=['AGENDADO', 'CONFIRMADO']
    ).select_related('cliente', 'profissional', 'servico').order_by('data_hora')[:5]
    
    # Agendamentos de hoje
    agendamentos_hoje_list = agendamentos_hoje.order_by('data_hora')
    
    context = {
        'stats': stats,
        'proximos_agendamentos': proximos_agendamentos,
        'agendamentos_hoje': agendamentos_hoje_list,
        'hoje': hoje,
    }
    
    return render(request, 'appointments/dashboard.html', context)