from datetime import datetime, time

from django import forms
from django.utils import timezone

from .models import Agendamento, Cliente, Profissional, Servico
from .utils import get_local_now, get_local_today


class AgendamentoForm(forms.ModelForm):
    # Campos separados para melhor UX
    data = forms.DateField(
        label="Data",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "min": get_local_today().strftime(
                    "%Y-%m-%d"
                ),  # Não permite datas passadas
            },
            format="%Y-%m-%d",  # Formato ISO para input type="date"
        ),
        input_formats=["%Y-%m-%d"],  # Aceita apenas formato ISO
        help_text="Selecione a data do agendamento",
    )

    hora = forms.TimeField(
        label="Horário",
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": "form-control",
                "step": "3600",  # Intervalos de 1 hora
            }
        ),
        help_text="Selecione o horário do agendamento (apenas horas cheias: 08:00, 09:00, etc.)",
    )

    class Meta:
        model = Agendamento
        fields = ["cliente", "profissional", "servico", "observacoes"]
        widgets = {
            "cliente": forms.Select(
                attrs={"class": "form-select", "placeholder": "Selecione o cliente"}
            ),
            "profissional": forms.Select(
                attrs={
                    "class": "form-select",
                    "placeholder": "Selecione o profissional",
                }
            ),
            "servico": forms.Select(
                attrs={"class": "form-select", "placeholder": "Selecione o serviço"}
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações adicionais (opcional)",
                }
            ),
        }
        labels = {
            "cliente": "Cliente",
            "profissional": "Profissional",
            "servico": "Serviço",
            "observacoes": "Observações",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar querysets para melhor performance
        self.fields["cliente"].queryset = Cliente.objects.filter(ativo=True).order_by(
            "nome"
        )
        self.fields["profissional"].queryset = Profissional.objects.filter(
            ativo=True
        ).order_by("nome")
        self.fields["servico"].queryset = Servico.objects.filter(ativo=True).order_by(
            "categoria", "nome"
        )

        # Se está editando um agendamento existente, separar data e hora
        if self.instance and self.instance.pk and self.instance.data_hora:
            # Converter para timezone local antes de separar data e hora
            data_hora_local = timezone.localtime(self.instance.data_hora)
            self.fields["data"].initial = data_hora_local.date()
            self.fields["hora"].initial = data_hora_local.time()
        else:
            # Valores padrão para novo agendamento
            now_local = get_local_now()
            self.fields["data"].initial = get_local_today()
            # Próximo horário comercial (próxima hora cheia)
            if now_local.hour < 8:
                self.fields["hora"].initial = time(8, 0)
            elif now_local.hour >= 18:
                # Se após 18h, sugere 8h do próximo dia
                self.fields["hora"].initial = time(8, 0)
            else:
                # Próxima hora cheia
                hour = now_local.hour + 1 if now_local.minute > 0 else now_local.hour
                self.fields["hora"].initial = time(hour, 0)

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        hora = cleaned_data.get("hora")
        profissional = cleaned_data.get("profissional")

        if hora:
            # Validar se o horário está em horas cheias (apenas :00)
            if hora.minute != 0:
                raise forms.ValidationError(
                    "O horário deve ser em horas cheias (exemplo: 08:00, 09:00, 10:00)."
                )

        if data and hora:
            # Combinar data e hora
            data_hora = timezone.make_aware(datetime.combine(data, hora))
            cleaned_data["data_hora"] = data_hora

            # Validações personalizadas
            now = timezone.now()

            # Não permitir agendamentos no passado
            if data_hora <= now:
                raise forms.ValidationError(
                    "Não é possível agendar para uma data/hora que já passou."
                )

            # Verificar se o profissional trabalha neste dia
            if profissional:
                dia_semana = data.isoweekday()  # 1=segunda, 7=domingo
                if dia_semana not in profissional.lista_dias_semana:
                    dias_map = {
                        "1": "Segunda-feira",
                        "2": "Terça-feira",
                        "3": "Quarta-feira",
                        "4": "Quinta-feira",
                        "5": "Sexta-feira",
                        "6": "Sábado",
                        "7": "Domingo",
                    }
                    raise forms.ValidationError(
                        f"{profissional.nome} não trabalha às {dias_map[str(dia_semana)]}s."
                    )

                # Verificar horário de trabalho
                if not (
                    profissional.horario_inicio <= hora <= profissional.horario_fim
                ):
                    raise forms.ValidationError(
                        f'{profissional.nome} trabalha das {profissional.horario_inicio.strftime("%H:%M")} '
                        f'às {profissional.horario_fim.strftime("%H:%M")}.'
                    )

                # Verificar conflitos de horário
                # FIXME: Melhorar essa validação para considerar duração do serviço
                conflitos = Agendamento.objects.filter(
                    profissional=profissional, data_hora=data_hora
                ).exclude(status__in=["CANCELADO", "NAO_COMPARECEU"])

                # Se estiver editando, excluir o próprio agendamento da verificação
                if self.instance and self.instance.pk:
                    conflitos = conflitos.exclude(pk=self.instance.pk)

                if conflitos.exists():
                    raise forms.ValidationError(
                        f"{profissional.nome} já possui um agendamento para este horário."
                    )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Definir data_hora combinada
        if hasattr(self, "cleaned_data") and "data_hora" in self.cleaned_data:
            instance.data_hora = self.cleaned_data["data_hora"]

        if commit:
            instance.save()
        return instance


class ClienteForm(forms.ModelForm):
    """Form personalizado para clientes com máscara de telefone"""

    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email", "endereco", "data_nascimento"]
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Digite o nome completo"}
            ),
            "telefone": forms.TextInput(
                attrs={
                    "type": "tel",
                    "class": "form-control",
                    "placeholder": "(11) 99999-9999",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "exemplo@email.com"}
            ),
            "endereco": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Endereço completo"}
            ),
            "data_nascimento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }


class ProfissionalForm(forms.ModelForm):
    """Form personalizado para profissionais com interface melhorada"""

    # Campo customizado para dias da semana
    dias_semana_choices = forms.MultipleChoiceField(
        choices=[
            ("1", "Segunda-feira"),
            ("2", "Terça-feira"),
            ("3", "Quarta-feira"),
            ("4", "Quinta-feira"),
            ("5", "Sexta-feira"),
            ("6", "Sábado"),
            ("7", "Domingo"),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=True,
        label="Dias da Semana",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Se está editando, carregar dados selecionados
        if self.instance and self.instance.pk:
            # Carregar dias selecionados
            if self.instance.dias_semana:
                self.fields["dias_semana_choices"].initial = [
                    str(dia) for dia in self.instance.lista_dias_semana
                ]

            # Carregar especialidades selecionadas
            self.fields["especialidades"].initial = self.instance.especialidades.all()

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Converter seleção de dias para string
        dias_selecionados = self.cleaned_data.get("dias_semana_choices", [])
        instance.dias_semana = ",".join(sorted(dias_selecionados))

        if commit:
            instance.save()
            # Salvar as especialidades (many-to-many)
            self.save_m2m()

        return instance

    class Meta:
        model = Profissional
        fields = [
            "nome",
            "telefone",
            "email",
            "especialidades",
            "horario_inicio",
            "horario_fim",
        ]
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Digite o nome completo"}
            ),
            "telefone": forms.TextInput(
                attrs={
                    "type": "tel",
                    "class": "form-control",
                    "placeholder": "(11) 99999-9999",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "exemplo@email.com"}
            ),
            "especialidades": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
            "horario_inicio": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "horario_fim": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
        }


class ServicoForm(forms.ModelForm):
    """Form personalizado para serviços"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campo duração sempre 60 minutos e somente leitura
        self.fields["duracao_minutos"].initial = 60
        self.fields["duracao_minutos"].widget.attrs.update(
            {"readonly": True, "value": 60}
        )
        self.fields["duracao_minutos"].help_text = (
            "Duração padrão: 60 minutos (não editável)"
        )

    class Meta:
        model = Servico
        fields = ["nome", "categoria", "descricao", "preco", "duracao_minutos"]
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome do serviço"}
            ),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição do serviço",
                }
            ),
            "preco": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "duracao_minutos": forms.NumberInput(
                attrs={
                    "class": "form-control bg-light",
                    "readonly": True,
                    "value": "60",
                }
            ),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.duracao_minutos = 60  # Garantir sempre 60 minutos
        if commit:
            instance.save()
        return instance
