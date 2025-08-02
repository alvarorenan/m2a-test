# Sistema de Agendamento para Salão de Beleza

Sistema web para gerenciar agendamentos de salão de beleza desenvolvido em Django.

## Funcionalidades

- CRUD de clientes, profissionais e serviços
- Sistema de agendamentos com validação de conflitos
- Dashboard com estatísticas básicas
- Relatórios por período
- Interface responsiva

## Tecnologias

- Django 4.2
- SQLite  
- Bootstrap 5
- Docker

## Como executar

### Docker (recomendado)
```bash
make build && make up
```

### Local
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py populate_data
python manage.py runserver
```

Acesso: http://localhost:8000  
Admin: http://localhost:8000/admin/ (admin/admin123)

## Comandos úteis

| Comando | Descrição |
|---------|-----------|
| `make up` | Inicia sistema completo |
| `make down` | Para o sistema |
| `make logs` | Ver logs |
| `make status` | Status do sistema |

## Estrutura

```
appointments/
├── models/       # Cliente, Profissional, Agendamento
├── views/        # Views organizadas por funcionalidade  
├── forms.py      # Formulários com validações
├── admin.py      # Interface administrativa
└── services/     # Lógica de negócio
```

## TODO

- [ ] Melhorar validação de conflitos considerando duração do serviço
- [ ] Adicionar notificações por email
- [ ] Implementar API REST
- [ ] Testes automatizados

## Observações

Projeto desenvolvido como teste técnico. Algumas melhorias foram identificadas durante o desenvolvimento e estão listadas nos TODOs acima.