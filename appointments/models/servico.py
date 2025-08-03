from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Servico(models.Model):
    """Model para representar serviços oferecidos pelo salão"""

    nome = models.CharField("Nome", max_length=100)
    descricao = models.TextField("Descrição", blank=True)
    preco = models.DecimalField(
        "Preço",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    duracao_minutos = models.PositiveIntegerField(
        "Duração (minutos)",
        default=60,
        validators=[MinValueValidator(1)],
        help_text="Todos os serviços têm duração padrão de 60 minutos",
    )
    categoria = models.CharField(
        "Categoria",
        max_length=50,
        choices=[
            ("CABELO", "Cabelo"),
            ("UNHAS", "Unhas"),
            ("ESTETICA", "Estética"),
            ("MASSAGEM", "Massagem"),
            ("OUTROS", "Outros"),
        ],
        default="OUTROS",
    )

    # Campos de auditoria
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True)
    data_atualizacao = models.DateTimeField("Data de Atualização", auto_now=True)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["categoria", "nome"]
        indexes = [
            models.Index(fields=["categoria"]),
            models.Index(fields=["ativo"]),
            models.Index(fields=["preco"]),
        ]

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"
