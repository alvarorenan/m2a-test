from django.db import models
from django.urls import reverse


class Profissional(models.Model):
    """Model para representar profissionais do salão"""
    nome = models.CharField('Nome', max_length=100)
    telefone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    especialidades = models.ManyToManyField(
        'Servico',
        verbose_name='Especialidades',
        help_text='Serviços que este profissional pode realizar'
    )
    
    # Horários de trabalho
    horario_inicio = models.TimeField('Horário de Início', default='08:00')
    horario_fim = models.TimeField('Horário de Fim', default='18:00')
    
    dias_semana = models.CharField(
        'Dias da Semana',
        max_length=20,
        default='1,2,3,4,5,6',  # Segunda a Sábado
        help_text='Dias da semana separados por vírgula (1=Segunda, 7=Domingo)'
    )
    
    # Campos de auditoria
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return self.nome

    @property
    def lista_dias_semana(self):
        """Retorna lista de dias da semana em que o profissional trabalha"""
        if not self.dias_semana:
            return []
        try:
            return [int(dia.strip()) for dia in self.dias_semana.split(',') if dia.strip().isdigit()]
        except (ValueError, AttributeError):
            return []