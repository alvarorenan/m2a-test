from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from ..models import Agendamento, Profissional, HistoricoAgendamento


class AgendamentoService:
    """Service para lógica de negócio relacionada a agendamentos"""
    
    @staticmethod
    def criar_agendamento(cliente, profissional, servico, data_hora, observacoes=None, preco_final=None):
        """Criar um novo agendamento com validações"""
        
        # Validações de negócio
        if not AgendamentoService.profissional_disponivel(profissional, data_hora, servico):
            raise ValueError('Profissional não está disponível neste horário ou há conflito com outro agendamento')
        
        if data_hora <= timezone.now():
            raise ValueError('Não é possível agendar para data/hora passada')
        
        # Criar agendamento
        agendamento = Agendamento.objects.create(
            cliente=cliente,
            profissional=profissional,
            servico=servico,
            data_hora=data_hora,
            observacoes=observacoes or '',
            preco_final=preco_final
        )
        
        # Criar histórico
        HistoricoAgendamento.objects.create(
            agendamento=agendamento,
            tipo_acao='CRIADO',
            descricao=f'Agendamento criado para {cliente.nome} com {profissional.nome}',
            status_novo=agendamento.status,
            usuario='Sistema'
        )
        
        return agendamento
    
    @staticmethod
    def profissional_disponivel(profissional, data_hora, servico=None):
        """Verificar se profissional está disponível (todos os serviços têm 60min)"""
        from datetime import datetime, timedelta
        
        # Verificar dia da semana
        dia_semana = data_hora.isoweekday()
        if dia_semana not in profissional.lista_dias_semana:
            return False
        
        # Verificar horário de trabalho
        if not (profissional.horario_inicio <= data_hora.time() < profissional.horario_fim):
            return False
        
        # Verificar se termina dentro do horário (todos os serviços têm 60min)
        fim_servico = data_hora + timedelta(hours=1)
        if fim_servico.time() > profissional.horario_fim:
            return False
        
        # Verificar se já há agendamento no mesmo horário exato
        conflito = Agendamento.objects.filter(
            profissional=profissional,
            data_hora=data_hora,
            status__in=['AGENDADO', 'CONFIRMADO', 'EM_ANDAMENTO']
        ).exists()
        
        return not conflito
    
    @staticmethod
    def alterar_status(agendamento, novo_status, usuario='Sistema'):
        """Alterar status do agendamento com validações"""
        
        status_anterior = agendamento.status
        
        # Validações específicas
        if novo_status == 'EM_ANDAMENTO' and agendamento.data_hora.date() < timezone.now().date():
            raise ValueError('Não é possível marcar como "Em Andamento" agendamentos de datas passadas')
        
        if novo_status == 'CONCLUIDO' and status_anterior not in ['CONFIRMADO', 'EM_ANDAMENTO']:
            raise ValueError('Só é possível concluir agendamentos confirmados ou em andamento')
        
        agendamento.status = novo_status
        agendamento.save()
        
        # Criar histórico
        descricoes = {
            'AGENDADO': 'Agendamento confirmado e agendado',
            'CONFIRMADO': 'Cliente confirmou o agendamento',
            'EM_ANDAMENTO': 'Atendimento iniciado',
            'CONCLUIDO': 'Atendimento finalizado com sucesso',
            'CANCELADO': 'Agendamento foi cancelado',
            'NAO_COMPARECEU': 'Cliente não compareceu ao agendamento'
        }
        
        HistoricoAgendamento.objects.create(
            agendamento=agendamento,
            tipo_acao='STATUS_ALTERADO',
            descricao=descricoes.get(novo_status, f'Status alterado para {agendamento.get_status_display()}'),
            status_anterior=status_anterior,
            status_novo=novo_status,
            usuario=usuario
        )
        
        return agendamento
    
    @staticmethod
    def get_horarios_disponiveis(profissional, data):
        """Obter horários disponíveis para um profissional em uma data (todos os serviços têm 60min)"""
        from datetime import datetime, timedelta
        
        # Verificar se trabalha no dia
        dia_semana = data.isoweekday()
        if dia_semana not in profissional.lista_dias_semana:
            return []
        
        # Gerar horários de trabalho (de hora em hora)
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
        
        # Buscar agendamentos já marcados nesta data (simples: só horário exato)
        agendamentos_ocupados = Agendamento.objects.filter(
            profissional=profissional,
            data_hora__date=data,
            status__in=['AGENDADO', 'CONFIRMADO', 'EM_ANDAMENTO']
        ).values_list('data_hora__time', flat=True)
        
        # Filtrar disponíveis
        horarios_disponiveis = [
            hora for hora in horarios_trabalho
            if hora not in agendamentos_ocupados
        ]
        
        return horarios_disponiveis