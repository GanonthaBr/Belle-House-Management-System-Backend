#!/bin/bash
# =============================================================================
# Belle House Backend - Deployment Script
# =============================================================================
# Usage: ./scripts/deploy.sh [--build]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Belle House Backend Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running with build flag
BUILD_FLAG=""
if [ "$1" == "--build" ]; then
    BUILD_FLAG="--build"
    echo -e "${YELLOW}Building containers...${NC}"
fi

# Ensure we're in the project directory
cd "$(dirname "$0")/.."

# Check for required files
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Copy .env.prod.example to .env and configure it."
    exit 1
fi

echo -e "\n${YELLOW}Step 1: Pulling latest code...${NC}"
git pull origin main

echo -e "\n${YELLOW}Step 2: Stopping existing containers...${NC}"
docker-compose down

echo -e "\n${YELLOW}Step 3: Starting containers...${NC}"
docker-compose up -d ${BUILD_FLAG}

echo -e "\n${YELLOW}Step 4: Waiting for database...${NC}"
sleep 10

echo -e "\n${YELLOW}Step 5: Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput

echo -e "\n${YELLOW}Step 6: Collecting static files...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput

echo -e "\n${YELLOW}Step 7: Checking container health...${NC}"
docker-compose ps

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

# Show logs
echo -e "\n${YELLOW}Recent logs:${NC}"
docker-compose logs --tail=20 web
