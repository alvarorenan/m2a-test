from django.db import models


class HistoricoAgendamento(models.Model):
    """Model para registrar histórico de mudanças nos agendamentos"""

    agendamento = models.ForeignKey(
        "Agendamento",
        on_delete=models.CASCADE,
        related_name="historico",
        verbose_name="Agendamento",
    )

    TIPO_ACAO_CHOICES = [
        ("CRIADO", "Agendamento Criado"),
        ("STATUS_ALTERADO", "Status Alterado"),
        ("DADOS_ALTERADOS", "Dados Alterados"),
        ("CANCELADO", "Cancelado"),
        ("REAGENDADO", "Reagendado"),
    ]

    tipo_acao = models.CharField(
        "Tipo de Ação", max_length=20, choices=TIPO_ACAO_CHOICES
    )

    descricao = models.TextField("Descrição", max_length=500)

    status_anterior = models.CharField(
        "Status Anterior",
        max_length=20,
        choices=[
            ("AGENDADO", "Agendado"),
            ("CONFIRMADO", "Confirmado"),
            ("EM_ANDAMENTO", "Em Andamento"),
            ("CONCLUIDO", "Concluído"),
            ("CANCELADO", "Cancelado"),
            ("NAO_COMPARECEU", "Não Compareceu"),
        ],
        blank=True,
        null=True,
    )

    status_novo = models.CharField(
        "Status Novo",
        max_length=20,
        choices=[
            ("AGENDADO", "Agendado"),
            ("CONFIRMADO", "Confirmado"),
            ("EM_ANDAMENTO", "Em Andamento"),
            ("CONCLUIDO", "Concluído"),
            ("CANCELADO", "Cancelado"),
            ("NAO_COMPARECEU", "Não Compareceu"),
        ],
        blank=True,
        null=True,
    )

    usuario = models.CharField(
        "Usuário", max_length=100, default="Sistema", help_text="Quem fez a alteração"
    )

    data_acao = models.DateTimeField("Data da Ação", auto_now_add=True)

    observacoes = models.TextField("Observações", blank=True)

    class Meta:
        verbose_name = "Histórico de Agendamento"
        verbose_name_plural = "Históricos de Agendamentos"
        ordering = ["-data_acao"]
        indexes = [
            models.Index(fields=["agendamento", "-data_acao"]),
        ]

    def __str__(self):
        return f"{self.agendamento} - {self.get_tipo_acao_display()}"
