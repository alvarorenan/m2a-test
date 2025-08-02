# ====================================
# 💄 Salon Management - Makefile
# ====================================

IMAGE_NAME = salon-management
CONTAINER_NAME = salon-app
PORT = 8000

.PHONY: help build up down restart flush load-data logs status clean

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

clean: ## Remove tudo (imagem + container)
	@echo "⚠️  Isso vai remover a imagem e todos os dados!"
	@read -p "Continuar? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@make down
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true