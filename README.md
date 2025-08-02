# Sistema de Agendamento para Salão de Beleza

Sistema web desenvolvido em Django para gerenciar agendamentos, clientes, profissionais e serviços de um salão de beleza.

## Funcionalidades

- **Gestão de Clientes**: Cadastro com dados pessoais e histórico
- **Profissionais**: Controle de especialidades e horários de trabalho
- **Serviços**: Catálogo com preços e categorias
- **Agendamentos**: Sistema com validação de conflitos e controle de status
- **Dashboard**: Estatísticas básicas e próximos agendamentos
- **Relatórios**: Serviços concluídos por período e performance

## Tecnologias

- **Backend**: Django 4.2 (Python 3.11+)
- **Banco**: SQLite com índices para performance
- **Frontend**: Bootstrap 5 + JavaScript
- **Containerização**: Docker
- **Automação**: Makefile

## Como executar

### Via Docker (recomendado)

```bash
# Ver comandos disponíveis
make help

# Construir e iniciar
make build && make up

# Verificar status
make status
```

### Execução local

```bash
# 1. Ambiente virtual
python -m venv venv
source venv/bin/activate

# 2. Dependências
pip install -r requirements.txt

# 3. Banco de dados
python manage.py migrate

# 4. Dados de exemplo
python manage.py populate_data

# 5. Executar
python manage.py runserver
```

**Acesso:**
- Sistema: http://localhost:8000
- Admin: http://localhost:8000/admin/ (admin/admin123)

## Comandos úteis (Makefile)

| Comando | Descrição |
|---------|-----------|
| `make up` | Inicia sistema completo com dados |
| `make down` | Para e remove container |
| `make logs` | Ver logs em tempo real |
| `make restart` | Reinicia o sistema |
| `make load-data` | Recarrega dados de exemplo |

## Dados de demonstração

O comando `populate_data` cria:
- 10 serviços categorizados
- 6 profissionais com especialidades
- 20 clientes com dados brasileiros
- ~160 agendamentos distribuídos em 45 dias

## Melhorias futuras

- [ ] **API REST** para integração mobile
- [ ] **Notificações** por email/SMS 
- [ ] **Calendário** integrado
- [ ] **Pagamentos** online
- [ ] **Relatórios** em PDF
- [ ] **Testes** automatizados

## TODOs e melhorias técnicas

- [ ] **FIXME**: Validação de conflitos deve considerar duração do serviço
- [ ] **TODO**: Refatorar campo `preco_final` (redundante com preço do serviço)
- [ ] **TODO**: Implementar testes unitários para models e forms
- [ ] **TODO**: Otimizar queries N+1 em relatórios
- [ ] **FIXME**: Melhorar validação de horários sobrepostos

## Estrutura do projeto

```
appointments/
├── models/          # Cliente, Profissional, Agendamento, etc
├── views/           # Views organizadas por funcionalidade
├── forms.py         # Formulários com validações personalizadas
├── admin.py         # Interface administrativa
├── services/        # Lógica de negócio
└── management/      # Comandos personalizados (populate_data)
```