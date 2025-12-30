# =============================================================================
# Belle House Backend - Makefile
# =============================================================================
# Commandes utilitaires pour le développement et le déploiement

.PHONY: help install run test lint migrate shell docker-up docker-down docker-build deploy backup

# Default target
help:
	@echo "Belle House Backend - Commandes disponibles:"
	@echo ""
	@echo "  Development:"
	@echo "    make install     - Installer les dépendances Python"
	@echo "    make run         - Lancer le serveur de développement"
	@echo "    make test        - Lancer les tests"
	@echo "    make lint        - Vérifier le code (flake8)"
	@echo "    make migrate     - Appliquer les migrations"
	@echo "    make shell       - Ouvrir un shell Django"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-up   - Démarrer les containers (dev)"
	@echo "    make docker-down - Arrêter les containers"
	@echo "    make docker-build- Reconstruire les containers"
	@echo "    make docker-logs - Afficher les logs"
	@echo ""
	@echo "  Production:"
	@echo "    make deploy      - Déployer en production"
	@echo "    make backup      - Sauvegarder la base de données"
	@echo ""

# =============================================================================
# Development Commands
# =============================================================================

install:
	pip install -r requirements.txt

run:
	python manage.py runserver

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=. --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

lint:
	flake8 . --exclude=venv,migrations,__pycache__

migrate:
	python manage.py makemigrations
	python manage.py migrate

shell:
	python manage.py shell

superuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput

# =============================================================================
# Docker Commands (Development)
# =============================================================================

docker-up:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Containers started. API available at http://localhost:8000"

docker-down:
	docker-compose down

docker-build:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec web python manage.py shell

docker-migrate:
	docker-compose exec web python manage.py migrate

docker-superuser:
	docker-compose exec web python manage.py createsuperuser

# =============================================================================
# Production Commands
# =============================================================================

deploy:
	./scripts/deploy.sh

deploy-build:
	./scripts/deploy.sh --build

backup:
	./scripts/backup_db.sh

restore:
	@echo "Usage: ./scripts/restore_db.sh <backup_file.sql.gz>"

ssl-init:
	@echo "Usage: ./scripts/init_ssl.sh <domain> <email>"

prod-logs:
	./scripts/logs.sh web -f

# =============================================================================
# Cleanup
# =============================================================================

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage

clean-docker:
	docker-compose down -v --remove-orphans
	docker system prune -f
