from django.http import JsonResponse
from datetime import datetime

from ..models import Profissional, Agendamento


def api_horarios_disponiveis(request):
    """API para retornar horários disponíveis para um profissional em uma data"""
    profissional_id = request.GET.get('profissional_id')
    data = request.GET.get('data')
    
    if not profissional_id or not data:
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
    
    try:
        profissional = Profissional.objects.get(id=profissional_id, ativo=True)
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
    except (Profissional.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Profissional ou data inválidos'}, status=400)
    
    # Verificar se o profissional trabalha neste dia da semana
    dia_semana = data_obj.isoweekday()  # 1=segunda, 7=domingo
    if dia_semana not in profissional.lista_dias_semana:
        return JsonResponse({'horarios': []})
    
    # Gerar horários de trabalho (de hora em hora - todos os serviços têm 60min)
    from datetime import time, timedelta
    horarios_trabalho = []
    hora_atual = profissional.horario_inicio
    
    while hora_atual < profissional.horario_fim:
        horarios_trabalho.append(hora_atual)
        # Adicionar 1 hora
        hour = hora_atual.hour + 1
        if hour < 24:
            hora_atual = hora_atual.replace(hour=hour)
        else:
            break
    
    # Buscar agendamentos já marcados nesta data (simples: só verificar horário exato)
    agendamentos_ocupados = Agendamento.objects.filter(
        profissional=profissional,
        data_hora__date=data_obj,
        status__in=['AGENDADO', 'CONFIRMADO', 'EM_ANDAMENTO']
    ).values_list('data_hora__time', flat=True)
    
    # Filtrar horários disponíveis (simples: horários não ocupados)
    horarios_disponiveis = [
        hora.strftime('%H:%M') for hora in horarios_trabalho
        if hora not in agendamentos_ocupados
    ]
    
    return JsonResponse({'horarios': horarios_disponiveis})