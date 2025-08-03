import random
import unicodedata
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from appointments.models import Agendamento, Cliente, Profissional, Servico


class Command(BaseCommand):
    help = "Popula o banco de dados com dados de exemplo para demonstração"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Limpa todos os dados antes de popular",
        )

    def normalizar_nome(self, nome):
        nome_normalizado = (
            unicodedata.normalize("NFKD", nome)
            .encode("ASCII", "ignore")
            .decode("utf-8")
        )
        return nome_normalizado

    def formatar_nome_para_email(self, nome):
        nome_normalizado = self.normalizar_nome(nome)
        # Substitui espaço por ponto e mantém apenas letras, números e pontos
        email_user = "".join(
            c if c.isalnum() or c == "." else "."
            for c in nome_normalizado.lower().replace(" ", ".")
        )
        # Remove pontos duplicados e bordas
        return ".".join(filter(None, email_user.split(".")))

    def gerar_email(self, nome, dominio):
        """Gera um endereço de email com base no nome e domínio fornecidos"""
        nome_formatado = self.formatar_nome_para_email(nome)
        return f"{nome_formatado}@{dominio}"

    def gerar_email_profissional(self, nome):
        """Gera um email para profissional usando o domínio salon.com"""
        return self.gerar_email(nome, "salon.com")

    def gerar_email_cliente(self, nome):
        """Gera um email para cliente usando o domínio gmail.com"""
        return self.gerar_email(nome, "gmail.com")

    def handle(self, *args, **options):
        # Configurar Faker para português brasileiro
        fake = Faker("pt_BR")
        Faker.seed(42)  # Para dados consistentes entre execuções

        if options["clear"]:
            self.stdout.write("Limpando dados existentes...")
            Agendamento.objects.all().delete()
            Cliente.objects.all().delete()
            Servico.objects.all().delete()
            Profissional.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Dados limpos com sucesso!"))

        self.stdout.write("Criando dados de exemplo...")

        # Criar serviços
        servicos_data = [
            {
                "nome": "Corte de Cabelo Feminino",
                "categoria": "CABELO",
                "preco": Decimal("45.00"),
                "duracao_minutos": 60,
                "descricao": "Corte personalizado para cabelo feminino",
            },
            {
                "nome": "Corte de Cabelo Masculino",
                "categoria": "CABELO",
                "preco": Decimal("25.00"),
                "duracao_minutos": 60,
                "descricao": "Corte tradicional masculino",
            },
            {
                "nome": "Escova e Prancha",
                "categoria": "CABELO",
                "preco": Decimal("35.00"),
                "duracao_minutos": 60,
                "descricao": "Escovação e finalização com prancha",
            },
            {
                "nome": "Coloração",
                "categoria": "CABELO",
                "preco": Decimal("80.00"),
                "duracao_minutos": 60,
                "descricao": "Coloração completa do cabelo",
            },
            {
                "nome": "Manicure",
                "categoria": "UNHAS",
                "preco": Decimal("20.00"),
                "duracao_minutos": 60,
                "descricao": "Cuidados e esmaltação das unhas das mãos",
            },
            {
                "nome": "Pedicure",
                "categoria": "UNHAS",
                "preco": Decimal("25.00"),
                "duracao_minutos": 60,
                "descricao": "Cuidados e esmaltação das unhas dos pés",
            },
            {
                "nome": "Unha em Gel",
                "categoria": "UNHAS",
                "preco": Decimal("50.00"),
                "duracao_minutos": 60,
                "descricao": "Aplicação de unhas em gel",
            },
            {
                "nome": "Limpeza de Pele",
                "categoria": "ESTETICA",
                "preco": Decimal("60.00"),
                "duracao_minutos": 60,
                "descricao": "Limpeza profunda da pele facial",
            },
            {
                "nome": "Massagem Relaxante",
                "categoria": "MASSAGEM",
                "preco": Decimal("70.00"),
                "duracao_minutos": 60,
                "descricao": "Massagem corporal relaxante",
            },
            {
                "nome": "Design de Sobrancelhas",
                "categoria": "ESTETICA",
                "preco": Decimal("30.00"),
                "duracao_minutos": 60,
                "descricao": "Design e modelagem de sobrancelhas",
            },
        ]

        servicos = []
        for servico_data in servicos_data:
            servico, created = Servico.objects.get_or_create(
                nome=servico_data["nome"], defaults=servico_data
            )
            servicos.append(servico)
            if created:
                self.stdout.write(f"  ✓ Serviço criado: {servico.nome}")

        # Criar profissionais com Faker
        especialidades_config = [
            ["CABELO", "ESTETICA"],
            ["CABELO"],
            ["UNHAS"],
            ["MASSAGEM", "ESTETICA"],
            ["CABELO", "UNHAS"],
            ["ESTETICA"],
            ["UNHAS", "ESTETICA"],
            ["CABELO", "MASSAGEM"],
            ["ESTETICA", "MASSAGEM"],
            ["CABELO", "ESTETICA", "UNHAS"],
        ]

        horarios_config = [
            (time(8, 0), time(18, 0), "1,2,3,4,5,6"),  # Segunda a sábado
            (time(9, 0), time(17, 0), "1,2,3,4,5"),  # Segunda a sexta
            (time(8, 0), time(16, 0), "1,2,3,4,5,6"),  # Segunda a sábado
            (time(10, 0), time(19, 0), "2,3,4,5,6"),  # Terça a sábado
            (time(7, 0), time(15, 0), "1,2,3,4,5"),  # Segunda a sexta
            (time(13, 0), time(21, 0), "3,4,5,6,7"),  # Quarta a domingo
            (time(8, 30), time(17, 30), "1,2,3,4,5"),  # Segunda a sexta (manhã/tarde)
            (time(14, 0), time(22, 0), "1,2,3,4,5,6"),  # Tarde/noite segunda a sábado
            (time(9, 30), time(18, 30), "2,3,4,5,6"),  # Terça a sábado
            (time(7, 30), time(16, 30), "1,2,3,4,5,6"),  # Segunda a sábado (cedo)
        ]

        # Número de profissionais desejado
        num_profissionais = 8

        profissionais_data = []
        for i in range(num_profissionais):
            nome = fake.name()
            # Usar módulo para evitar index out of range
            config_index = i % len(horarios_config)
            horario_inicio, horario_fim, dias_semana = horarios_config[config_index]
            especialidades = especialidades_config[config_index]

            profissionais_data.append(
                {
                    "nome": nome,
                    "telefone": fake.phone_number(),
                    "email": self.gerar_email_profissional(nome),
                    "horario_inicio": horario_inicio,
                    "horario_fim": horario_fim,
                    "dias_semana": dias_semana,
                    "especialidades": especialidades,
                }
            )

        profissionais = []
        for prof_data in profissionais_data:
            especialidades = prof_data.pop("especialidades")
            profissional, created = Profissional.objects.get_or_create(
                nome=prof_data["nome"], defaults=prof_data
            )

            if created:
                # Adicionar especialidades
                servicos_especialidade = [
                    s for s in servicos if s.categoria in especialidades
                ]
                profissional.especialidades.set(servicos_especialidade)
                self.stdout.write(f"  ✓ Profissional criado: {profissional.nome}")

            profissionais.append(profissional)

        # Criar clientes com Faker
        clientes = []
        for i in range(20):  # Criar 20 clientes
            nome = fake.name()

            # Criar dados mais completos
            cliente_data = {
                "nome": nome,
                "telefone": fake.phone_number(),
                "email": self.gerar_email_cliente(nome),
                "endereco": fake.address(),
                "data_nascimento": fake.date_of_birth(minimum_age=18, maximum_age=80),
                "observacoes": (
                    fake.text(max_nb_chars=100) if random.choice([True, False]) else ""
                ),
            }

            cliente, created = Cliente.objects.get_or_create(
                nome=cliente_data["nome"], defaults=cliente_data
            )
            clientes.append(cliente)
            if created:
                self.stdout.write(f"  ✓ Cliente criado: {cliente.nome}")

        # Criar agendamentos (últimos 30 dias + próximos 15 dias)
        self.stdout.write("Criando agendamentos...")

        agendamentos_criados = 0
        hoje = timezone.now().date()

        # Agendamentos passados (últimos 30 dias)
        for dias_atras in range(30, 0, -1):
            data = hoje - timedelta(days=dias_atras)

            # 3-8 agendamentos por dia
            num_agendamentos = random.randint(3, 8)

            for _ in range(num_agendamentos):
                cliente = random.choice(clientes)
                profissional = random.choice(profissionais)
                servicos_prof = list(profissional.especialidades.all())

                if servicos_prof:
                    servico = random.choice(servicos_prof)

                    # Horário aleatório dentro do horário de trabalho
                    hora_inicio = profissional.horario_inicio.hour
                    hora_fim = profissional.horario_fim.hour - 1
                    hora = random.randint(hora_inicio, hora_fim)

                    data_hora = timezone.make_aware(
                        datetime.combine(data, time(hora, 0))
                    )

                    # Status baseado na data
                    if dias_atras > 7:
                        status = random.choice(
                            ["CONCLUIDO", "CONCLUIDO", "CONCLUIDO", "CANCELADO"]
                        )
                    else:
                        status = random.choice(
                            ["CONCLUIDO", "CANCELADO", "NAO_COMPARECEU"]
                        )

                    # Verificar se não há conflito
                    if not Agendamento.objects.filter(
                        profissional=profissional, data_hora=data_hora
                    ).exists():
                        Agendamento.objects.create(
                            cliente=cliente,
                            profissional=profissional,
                            servico=servico,
                            data_hora=data_hora,
                            status=status,
                        )
                        agendamentos_criados += 1

        # Agendamentos para hoje
        agendamentos_hoje = 0
        data_hoje = hoje
        dia_semana_hoje = data_hoje.isoweekday()
        profissionais_trabalham_hoje = [
            p for p in profissionais if dia_semana_hoje in p.lista_dias_semana
        ]

        if profissionais_trabalham_hoje:
            # Garantir exatamente 3 agendamentos para hoje
            tentativas_max = 20  # Para evitar loop infinito
            while agendamentos_hoje < 3 and tentativas_max > 0:
                tentativas_max -= 1

                cliente = random.choice(clientes)
                profissional = random.choice(profissionais_trabalham_hoje)
                servicos_prof = list(profissional.especialidades.all())

                if servicos_prof:
                    servico = random.choice(servicos_prof)

                    # Horário aleatório dentro do horário de trabalho
                    hora_inicio = profissional.horario_inicio.hour
                    hora_fim = profissional.horario_fim.hour - 1

                    # Evitar horários que já passaram hoje
                    hora_atual = timezone.now().hour
                    if hora_atual > hora_inicio:
                        hora_inicio = min(hora_atual + 1, hora_fim)

                    # Se não há horários disponíveis, usar todo o range
                    if hora_inicio > hora_fim:
                        hora_inicio = profissional.horario_inicio.hour
                        hora_fim = profissional.horario_fim.hour - 1

                    hora = random.randint(hora_inicio, hora_fim)

                    data_hora = timezone.make_aware(
                        datetime.combine(data_hoje, time(hora, 0))
                    )

                    # Status para hoje baseado na hora
                    if hora < hora_atual:
                        # Horários que já passaram hoje
                        status = random.choice(
                            ["CONCLUIDO", "CONCLUIDO", "EM_ANDAMENTO", "CANCELADO"]
                        )
                    elif hora == hora_atual:
                        # Horário atual
                        status = random.choice(["EM_ANDAMENTO", "CONFIRMADO"])
                    else:
                        # Horários futuros hoje
                        status = random.choice(["AGENDADO", "CONFIRMADO", "CONFIRMADO"])

                    # Verificar se não há conflito (mesma data/hora/profissional)
                    if not Agendamento.objects.filter(
                        profissional=profissional, data_hora=data_hora
                    ).exists():
                        Agendamento.objects.create(
                            cliente=cliente,
                            profissional=profissional,
                            servico=servico,
                            data_hora=data_hora,
                            status=status,
                        )
                        agendamentos_criados += 1
                        agendamentos_hoje += 1

        # Agendamentos futuros (máximo 4 no total)
        agendamentos_futuros = 0
        for dias_futuro in range(1, 8):  # Próximos 7 dias
            if agendamentos_futuros >= 4:
                break

            data = hoje + timedelta(days=dias_futuro)

            # Verificar se é dia de trabalho para algum profissional
            dia_semana = data.isoweekday()
            profissionais_trabalham = [
                p for p in profissionais if dia_semana in p.lista_dias_semana
            ]

            if profissionais_trabalham:
                # 1 agendamento por dia até completar 4
                num_agendamentos = 1

                for _ in range(num_agendamentos):
                    if agendamentos_futuros >= 4:
                        break

                    cliente = random.choice(clientes)
                    profissional = random.choice(profissionais_trabalham)
                    servicos_prof = list(profissional.especialidades.all())

                    if servicos_prof:
                        servico = random.choice(servicos_prof)

                        # Horário aleatório dentro do horário de trabalho
                        hora_inicio = profissional.horario_inicio.hour
                        hora_fim = profissional.horario_fim.hour - 1

                        if hora_inicio <= hora_fim:
                            hora = random.randint(hora_inicio, hora_fim)
                        else:
                            continue  # Pular se não há horários disponíveis

                        data_hora = timezone.make_aware(
                            datetime.combine(data, time(hora, 0))
                        )

                        # Status para agendamentos futuros
                        if dias_futuro <= 2:  # Próximos 2 dias
                            status = random.choice(
                                ["AGENDADO", "CONFIRMADO", "CONFIRMADO"]
                            )
                        else:  # Dias mais distantes
                            status = random.choice(
                                ["AGENDADO", "AGENDADO", "CONFIRMADO"]
                            )

                        # Verificar se não há conflito
                        if not Agendamento.objects.filter(
                            profissional=profissional, data_hora=data_hora
                        ).exists():
                            Agendamento.objects.create(
                                cliente=cliente,
                                profissional=profissional,
                                servico=servico,
                                data_hora=data_hora,
                                status=status,
                            )
                            agendamentos_criados += 1
                            agendamentos_futuros += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Dados criados com sucesso usando Faker!\n"
                f"📊 Resumo:\n"
                f"  • {len(servicos)} serviços categorizados\n"
                f"  • {num_profissionais} profissionais com horários variados\n"
                f"  • {len(clientes)} clientes com dados completos\n"
                f"  • {agendamentos_criados} agendamentos realistas\n"
                f"\n🚀 O sistema está pronto para demonstração!"
            )
        )
