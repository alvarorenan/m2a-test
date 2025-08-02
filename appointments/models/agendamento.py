from django.db import models
from django.urls import reverse


class Agendamento(models.Model):
    """Model para representar agendamentos"""
    
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('CONFIRMADO', 'Confirmado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
        ('NAO_COMPARECEU', 'Não Compareceu'),
    ]
    
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        verbose_name='Cliente'
    )
    profissional = models.ForeignKey(
        'Profissional',
        on_delete=models.CASCADE,
        verbose_name='Profissional'
    )
    servico = models.ForeignKey(
        'Servico',
        on_delete=models.CASCADE,
        verbose_name='Serviço'
    )
    
    data_hora = models.DateTimeField('Data e Hora')
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGENDADO'
    )
    
    observacoes = models.TextField('Observações', blank=True)
    preco_final = models.DecimalField(
        'Preço Final',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Deixe vazio para usar o preço padrão do serviço'
    )
    
    # Campos de auditoria
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-data_hora']
        indexes = [
            # Índices para performance em consultas comuns
            models.Index(fields=['data_hora']),
            models.Index(fields=['status']),
            models.Index(fields=['profissional', 'data_hora']),
            models.Index(fields=['cliente', 'data_hora']),
            models.Index(fields=['status', 'data_hora']),
            # Índice composto para relatórios de serviços concluídos
            models.Index(fields=['status', 'data_hora', 'servico']),
        ]
        constraints = [
            # Evita agendamentos duplicados para o mesmo profissional no mesmo horário
            models.UniqueConstraint(
                fields=['profissional', 'data_hora'],
                condition=~models.Q(status__in=['CANCELADO', 'NAO_COMPARECEU']),
                name='unique_profissional_datetime_active'
            )
        ]

    def __str__(self):
        return f"{self.cliente.nome} - {self.servico.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Se preço final não foi definido, usa o preço do serviço
        if self.preco_final is None:
            self.preco_final = self.servico.preco
        super().save(*args, **kwargs)

    @property
    def data_hora_fim(self):
        """Calcula o horário de fim baseado na duração do serviço"""
        from datetime import timedelta
        return self.data_hora + timedelta(minutes=self.servico.duracao_minutos)
