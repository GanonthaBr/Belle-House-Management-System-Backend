#!/bin/bash
# =============================================================================
# Belle House Backend - Create Superuser Script
# =============================================================================
# Usage: ./scripts/create_superuser.sh

set -e

echo "Creating Django superuser..."

docker-compose exec web python manage.py createsuperuser

echo "Superuser created successfully!"
