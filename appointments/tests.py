from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AgendamentoForm
from .models import Agendamento, Cliente, Profissional, Servico
from .utils import get_local_now, get_local_today


class ClienteModelTest(TestCase):
    """Testes para o model Cliente"""

    def test_cliente_creation(self):
        """Testa criação de cliente"""
        cliente = Cliente.objects.create(
            nome="João Silva", telefone="(11) 99999-9999", email="joao@example.com"
        )
        self.assertEqual(cliente.nome, "João Silva")
        self.assertTrue(cliente.ativo)
        self.assertIsNotNone(cliente.data_cadastro)

    def test_cliente_str(self):
        """Testa representação string do cliente"""
        cliente = Cliente.objects.create(
            nome="Maria Santos", telefone="(11) 88888-8888"
        )
        self.assertEqual(str(cliente), "Maria Santos")


class ProfissionalModelTest(TestCase):
    """Testes para o model Profissional"""

    def test_profissional_creation(self):
        """Testa criação de profissional"""
        profissional = Profissional.objects.create(
            nome="Ana Costa",
            telefone="(11) 77777-7777",
            horario_inicio=time(8, 0),
            horario_fim=time(18, 0),
            dias_semana="1,2,3,4,5",
        )
        self.assertEqual(profissional.nome, "Ana Costa")
        self.assertEqual(profissional.horario_inicio, time(8, 0))
        self.assertTrue(profissional.ativo)

    def test_lista_dias_semana(self):
        """Testa método lista_dias_semana"""
        profissional = Profissional.objects.create(
            nome="Test Prof", telefone="(11) 77777-7777", dias_semana="1,2,3,4,5"
        )
        dias = profissional.lista_dias_semana
        self.assertEqual(dias, [1, 2, 3, 4, 5])


class ServicoModelTest(TestCase):
    """Testes para o model Servico"""

    def test_servico_creation(self):
        """Testa criação de serviço"""
        servico = Servico.objects.create(
            nome="Corte de Cabelo", preco=Decimal("30.00"), categoria="CABELO"
        )
        self.assertEqual(servico.nome, "Corte de Cabelo")
        self.assertEqual(servico.preco, Decimal("30.00"))
        self.assertEqual(servico.duracao_minutos, 60)  # Padrão
        self.assertTrue(servico.ativo)

    def test_servico_str(self):
        """Testa representação string do serviço"""
        servico = Servico.objects.create(
            nome="Manicure", preco=Decimal("25.00"), categoria="UNHAS"
        )
        expected = "Manicure - R$ 25.00"
        self.assertEqual(str(servico), expected)


class AgendamentoModelTest(TestCase):
    """Testes para o model Agendamento"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome="Pedro Lima", telefone="(11) 66666-6666"
        )
        self.servico = Servico.objects.create(
            nome="Corte", preco=Decimal("30.00"), categoria="CABELO"
        )
        self.profissional = Profissional.objects.create(
            nome="Carlos", telefone="(11) 55555-5555"
        )

        amanha = get_local_today() + timedelta(days=1)
        self.data_hora = timezone.make_aware(datetime.combine(amanha, time(14, 0)))

    def test_agendamento_creation(self):
        """Testa criação de agendamento"""
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data_hora=self.data_hora,
        )
        self.assertEqual(agendamento.status, "AGENDADO")
        self.assertEqual(agendamento.preco_final, self.servico.preco)

    def test_data_hora_fim(self):
        """Testa cálculo de data_hora_fim"""
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data_hora=self.data_hora,
        )
        expected_fim = self.data_hora + timedelta(minutes=self.servico.duracao_minutos)
        self.assertEqual(agendamento.data_hora_fim, expected_fim)


class AgendamentoFormTest(TestCase):
    """Testes para o formulário de agendamento"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome="Test Cliente", telefone="(11) 99999-9999"
        )
        self.servico = Servico.objects.create(
            nome="Test Serviço", preco=Decimal("50.00"), categoria="CABELO"
        )
        self.profissional = Profissional.objects.create(
            nome="Test Profissional",
            telefone="(11) 88888-8888",
            dias_semana="1,2,3,4,5",
        )
        self.profissional.especialidades.add(self.servico)

    def test_form_hora_com_minutos_invalida(self):
        """Testa validação de hora com minutos (deve ser rejeitada)"""
        amanha = get_local_today() + timedelta(days=1)

        form_data = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": amanha,
            "hora": time(14, 30),  # Deve ser rejeitada
            "observacoes": "Teste",
        }

        form = AgendamentoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("O horário deve ser em horas cheias", str(form.errors))


class DashboardViewTest(TestCase):
    """Testes para a view do dashboard"""

    def test_dashboard_loads(self):
        """Testa se o dashboard carrega corretamente"""
        client = Client()
        response = client.get(reverse("appointments:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")


class TimezoneUtilsTest(TestCase):
    """Testes para utilitários de timezone"""

    def test_get_local_today(self):
        """Testa se get_local_today retorna data local"""
        today = get_local_today()
        self.assertIsInstance(today, date)

    def test_get_local_now(self):
        """Testa se get_local_now retorna datetime local"""
        now = get_local_now()
        self.assertIsInstance(now, datetime)
        self.assertEqual(str(now.tzinfo), "America/Sao_Paulo")


class AgendamentoWorkflowTest(TestCase):
    """Testes de workflow de agendamento"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome="Workflow Cliente", telefone="(11) 99999-9999"
        )
        self.servico = Servico.objects.create(
            nome="Workflow Serviço", preco=Decimal("40.00"), categoria="CABELO"
        )
        self.profissional = Profissional.objects.create(
            nome="Workflow Prof", telefone="(11) 88888-8888"
        )

        amanha = get_local_today() + timedelta(days=1)
        self.data_hora = timezone.make_aware(datetime.combine(amanha, time(15, 0)))

    def test_workflow_status(self):
        """Testa mudança de status do agendamento"""
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data_hora=self.data_hora,
        )

        # Status inicial
        self.assertEqual(agendamento.status, "AGENDADO")

        # Confirmar
        agendamento.status = "CONFIRMADO"
        agendamento.save()
        self.assertEqual(agendamento.status, "CONFIRMADO")

        # Concluir
        agendamento.status = "CONCLUIDO"
        agendamento.save()
        self.assertEqual(agendamento.status, "CONCLUIDO")


class RelatorioViewTest(TestCase):
    """Testes para views de relatórios"""

    def test_relatorio_loads(self):
        """Testa se a view de relatórios carrega"""
        client = Client()
        response = client.get(reverse("appointments:relatorio_servicos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório")
