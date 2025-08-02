# 💄 Sistema de Agendamento para Salão de Beleza

## 📋 Introdução

Sistema completo para gerenciamento de agendamentos em salões de beleza, desenvolvido com Django 4.2. Oferece uma interface moderna e intuitiva para controle de clientes, profissionais, serviços e agendamentos.

## 📖 Sumário

- [🎯 Principais Funcionalidades](#-principais-funcionalidades)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [🚀 Como Executar o Projeto](#-como-executar-o-projeto)
- [🔮 Melhorias Futuras](#-melhorias-futuras)
- [📊 Dados de Demonstração](#-dados-de-demonstração)
- [⚡ Performance e Otimização](#-performance-e-otimização)
- [🏗️ Estrutura do Projeto](#️-estrutura-do-projeto)
- [🤝 Contribuindo](#-contribuindo)

## 🎯 Principais Funcionalidades

### Gestão Completa
- **Clientes**: Cadastro com dados pessoais e histórico de agendamentos
- **Profissionais**: Controle de especialidades, horários de trabalho e agenda
- **Serviços**: Catálogo com preços, durações e categorias organizadas
- **Agendamentos**: Sistema inteligente com validação de conflitos e controle de status

### Dashboard e Relatórios
- Painel principal com estatísticas em tempo real
- **Relatórios de serviços concluídos por período**
- Relatórios de performance por profissional
- Análise de receita e serviços mais solicitados
- Histórico completo de alterações nos agendamentos

### Interface Amigável
- Design responsivo com Bootstrap 5
- Menu organizado por categorias
- Filtros avançados e busca em tempo real
- Ações rápidas para atualização de status

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 4.2 (Python 3.11+)
- **Banco de Dados**: SQLite com índices otimizados para alta performance
- **Frontend**: Bootstrap 5 + JavaScript
- **Ambiente**: venv para isolamento de dependências
- **Containerização**: Docker
- **Automação**: Makefile para comandos facilitados

## 🚀 Como Executar o Projeto

### Opção 1: Via Docker (Recomendado)

O projeto inclui um **Makefile** que simplifica todos os comandos:

```bash
# Ver todos os comandos disponíveis
make help

# Construir e iniciar o sistema completo
make build && make up

# Verificar status
make status

# Ver logs em tempo real
make logs

# Parar o sistema
make down
```

Após executar `make up`, o sistema estará disponível em:
- **Aplicação**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/ (admin/admin123)

### Opção 2: Execução Local

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar banco de dados
python manage.py migrate

# 4. Carregar dados de exemplo
python manage.py populate_data

# 5. Criar superusuário (opcional)
python manage.py createsuperuser

# 6. Executar servidor
python manage.py runserver

# Acesse: http://localhost:8000
```

### Comandos Úteis do Makefile

| Comando | Descrição |
|---------|-----------|
| `make build` | Constrói a imagem Docker |
| `make up` | Inicia sistema completo (com dados) |
| `make down` | Para e remove container |
| `make restart` | Reinicia o sistema |
| `make logs` | Mostra logs em tempo real |
| `make status` | Verifica se está rodando |
| `make load-data` | Recarrega dados de exemplo |
| `make clean` | Remove tudo (imagem + dados) |

## 🔮 Melhorias Futuras

### Próximas Implementações
- [ ] **API REST** para integração mobile
- [ ] **Notificações** por email/SMS para clientes
- [ ] **Calendário integrado** com sincronização
- [ ] **Sistema de pagamentos** online
- [ ] **Relatórios em PDF** para impressão
- [ ] **App mobile** React Native

### Funcionalidades Avançadas
- [ ] **Autenticação social** (Google, Facebook)
- [ ] **Backup automático** do banco de dados
- [ ] **Multi-tenancy** para múltiplos salões
- [ ] **Integração com WhatsApp** Business
- [ ] **Sistema de fidelidade** para clientes
- [ ] **Análise preditiva** de demanda

## 📊 Dados de Demonstração

O sistema inclui um comando para popular o banco com dados realistas:

```bash
# Local
python manage.py populate_data

# Docker
make load-data
```

**Dados criados automaticamente:**
- 10 serviços categorizados (cabelo, unhas, estética, massagem)
- 6 profissionais com especialidades variadas
- 20 clientes com dados brasileiros realistas
- ~160 agendamentos distribuídos em 45 dias

## ⚡ Performance e Otimização

Sistema otimizado para lidar com milhares de agendamentos de forma eficiente.

### Estratégias Implementadas
- **Índices de banco** estratégicos em campos críticos (data_hora, status, profissional)
- **Select_related** para evitar queries N+1 nos relatórios
- **Paginação** em listagens para grandes volumes
- **Queries otimizadas** nos relatórios de serviços concluídos por período

### Testando Performance
```bash
# Gerar mais dados para teste
python manage.py populate_data --large

# Os relatórios continuam rápidos mesmo com milhares de registros
```

## 🏗️ Estrutura do Projeto

```
salon_management/
├── appointments/           # App principal
│   ├── models/            # Modelos (Cliente, Profissional, Agendamento)
│   ├── views/             # Views organizadas por funcionalidade
│   ├── services/          # Lógica de negócio
│   └── management/        # Comandos personalizados
├── templates/             # Templates HTML
├── static/                # CSS, JS, imagens
├── requirements.txt       # Dependências Python
├── Dockerfile            # Configuração Docker
├── Makefile              # Comandos automatizados
└── README.md             # Este arquivo
```
