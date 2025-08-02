from django.db import models
from django.urls import reverse


class Cliente(models.Model):
    """Model para representar clientes do salão"""
    nome = models.CharField('Nome', max_length=100)
    telefone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    endereco = models.TextField('Endereço', blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # Campos de auditoria
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['telefone']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return self.nome
