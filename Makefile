# ====================================
# 💄 Salon Management - Makefile
# ====================================

IMAGE_NAME = salon-management
CONTAINER_NAME = salon-app
PORT = 8000

.PHONY: help build up down restart flush load-data logs status clean test test-local test-docker test-coverage format

help: ## Mostra comandos disponíveis
	@echo "💄 Sistema de Agendamento - Comandos Docker"
	@echo "==========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
	@echo ""
	@echo "🚀 Início rápido: make build && make up"

build: ## Constrói a imagem Docker
	docker build -t $(IMAGE_NAME) .

up: ## Inicia sistema completo (migrate + dados)
	@make down 2>/dev/null || true
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):$(PORT) $(IMAGE_NAME)
	@sleep 3
	docker exec $(CONTAINER_NAME) python manage.py migrate
	docker exec $(CONTAINER_NAME) python manage.py populate_data
	@docker exec $(CONTAINER_NAME) python manage.py createsuperuser --no-input --username admin --email admin@salon.com 2>/dev/null || true
	@docker exec $(CONTAINER_NAME) python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); u.set_password('admin123'); u.save()" 2>/dev/null || true
	@echo ""
	@echo "✅ Sistema rodando: http://localhost:$(PORT)"
	@echo "🔐 Admin: http://localhost:$(PORT)/admin/ (admin/admin123)"

down: ## Para e remove o container
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true

restart: ## Reinicia o container
	@make down
	@make up

flush: ## Limpa banco de dados
	@echo "⚠️  Isso vai apagar TODOS os dados!"
	@read -p "Continuar? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker exec $(CONTAINER_NAME) python manage.py flush --noinput

load-data: ## Carrega dados de exemplo
	docker exec $(CONTAINER_NAME) python manage.py populate_data

logs: ## Mostra logs em tempo real
	docker logs -f $(CONTAINER_NAME)

status: ## Status do sistema
	@if docker ps --filter "name=$(CONTAINER_NAME)" --format "{{.Names}}" | grep -q $(CONTAINER_NAME); then \
		echo "🟢 Sistema rodando"; \
		echo "🌐 http://localhost:$(PORT)"; \
		echo "🔐 http://localhost:$(PORT)/admin/"; \
	else \
		echo "🔴 Sistema parado"; \
		echo "💡 Execute: make up"; \
	fi

test-local: ## Executa testes localmente (ambiente virtual)
	@if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
		echo "🧪 Executando testes localmente..."; \
		. venv/bin/activate && python manage.py test appointments.tests --verbosity=2 --keepdb; \
		echo "✅ Testes locais concluídos"; \
	else \
		echo "❌ Ambiente virtual não encontrado. Use 'make test-docker'"; \
	fi

test-docker: ## Executa testes no Docker
	@if docker ps --filter "name=$(CONTAINER_NAME)" --format "{{.Names}}" | grep -q $(CONTAINER_NAME); then \
		echo "🧪 Executando testes no Docker..."; \
		docker exec $(CONTAINER_NAME) python manage.py test appointments.tests --verbosity=2 --keepdb; \
		echo "✅ Testes Docker concluídos"; \
	else \
		echo "❌ Container não está rodando. Execute 'make up' primeiro"; \
	fi

test: ## Executa testes (detecta ambiente automaticamente)
	@if docker ps --filter "name=$(CONTAINER_NAME)" --format "{{.Names}}" | grep -q $(CONTAINER_NAME); then \
		echo "🐳 Docker detectado - executando no container..."; \
		make test-docker; \
	elif [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
		echo "🐍 Ambiente virtual detectado - executando localmente..."; \
		make test-local; \
	else \
		echo "❌ Nenhum ambiente encontrado!"; \
		echo "💡 Execute 'make up' (Docker) ou ative o venv"; \
		exit 1; \
	fi

test-coverage: ## Executa testes com relatório de cobertura
	@if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
		echo "🧪 Executando testes com cobertura..."; \
		. venv/bin/activate && python -m pip install coverage >/dev/null 2>&1 || true; \
		. venv/bin/activate && coverage run --source='.' manage.py test appointments.tests --keepdb; \
		. venv/bin/activate && coverage report --omit="venv/*,*/migrations/*,manage.py,*/settings.py,*/wsgi.py,*/asgi.py"; \
		. venv/bin/activate && coverage html --omit="venv/*,*/migrations/*,manage.py,*/settings.py,*/wsgi.py,*/asgi.py"; \
		echo "📊 Relatório HTML gerado em: htmlcov/index.html"; \
	else \
		echo "❌ Ambiente virtual não encontrado para coverage"; \
	fi

format: ## Formata código Python local (isort + black + flake8)
	@if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
		echo "🎨 Formatando código Python local..."; \
		echo "📦 Instalando ferramentas no ambiente virtual..."; \
		. venv/bin/activate && pip install black isort flake8 -q; \
		echo "📦 Organizando imports..."; \
		. venv/bin/activate && isort . --profile black --skip venv; \
		echo "⚫ Formatando com Black..."; \
		. venv/bin/activate && black --exclude "(migrations|venv)" --line-length 88 .; \
		echo "🔍 Verificando com Flake8..."; \
		. venv/bin/activate && flake8 --exclude=migrations,venv --max-line-length=88 --extend-ignore=E203,W503,E501,F403,F405; \
		echo "✅ Formatação local concluída!"; \
	else \
		echo "❌ Ambiente virtual não encontrado!"; \
		echo "💡 Crie um ambiente virtual:"; \
		echo "   python3 -m venv venv"; \
		echo "   source venv/bin/activate"; \
		echo "   pip install -r requirements.txt"; \
	fi

clean: ## Remove tudo (imagem + container)
	@echo "⚠️  Isso vai remover a imagem e todos os dados!"
	@read -p "Continuar? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@make down
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true