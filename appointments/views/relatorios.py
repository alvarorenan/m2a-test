from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime, timedelta

from ..models import Agendamento, Profissional


def relatorio_servicos(request):
    """Relatório de serviços concluídos com foco em performance"""
    # Parâmetros de filtro
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    profissional_id = request.GET.get('profissional')
    
    # Data padrão: último mês
    if not data_inicio:
        data_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = timezone.now().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Query otimizada com índices
    queryset = Agendamento.objects.filter(
        status='CONCLUIDO',
        data_hora__date__gte=data_inicio,
        data_hora__date__lte=data_fim
    ).select_related('servico', 'profissional', 'cliente')
    
    if profissional_id:
        queryset = queryset.filter(profissional_id=profissional_id)
    
    # Agregações para relatório
    servicos_stats = queryset.values(
        'servico__nome', 'servico__categoria'
    ).annotate(
        total_servicos=Count('id'),
        receita_total=Sum('preco_final')
    ).order_by('-total_servicos')
    
    profissionais_stats = queryset.values(
        'profissional__nome'
    ).annotate(
        total_servicos=Count('id'),
        receita_total=Sum('preco_final')
    ).order_by('-total_servicos')
    
    # Estatísticas gerais
    stats_gerais = queryset.aggregate(
        total_agendamentos=Count('id'),
        receita_total=Sum('preco_final'),
        ticket_medio=Sum('preco_final') / Count('id') if queryset.exists() else 0
    )
    
    # Agendamentos por dia (para gráfico)
    agendamentos_por_dia = queryset.extra(
        select={'data': 'DATE(data_hora)'}
    ).values('data').annotate(
        total=Count('id'),
        receita=Sum('preco_final')
    ).order_by('data')
    
    context = {
        'servicos_stats': servicos_stats,
        'profissionais_stats': profissionais_stats,
        'stats_gerais': stats_gerais,
        'agendamentos_por_dia': list(agendamentos_por_dia),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'profissional_id': profissional_id,
        'profissionais': Profissional.objects.filter(ativo=True).order_by('nome'),
        'periodo_dias': (data_fim - data_inicio).days + 1,
    }
    
    return render(request, 'appointments/relatorio_servicos.html', context)