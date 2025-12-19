#!/bin/bash
# =============================================================================
# Belle House Backend - View Logs Script
# =============================================================================
# Usage: ./scripts/logs.sh [service] [--follow]
# Examples:
#   ./scripts/logs.sh           # All logs
#   ./scripts/logs.sh web       # Web container logs
#   ./scripts/logs.sh web -f    # Follow web logs

SERVICE=$1
FOLLOW=""

if [ "$2" == "-f" ] || [ "$2" == "--follow" ]; then
    FOLLOW="-f"
fi

if [ -z "$SERVICE" ]; then
    docker-compose logs --tail=100 ${FOLLOW}
else
    docker-compose logs --tail=100 ${FOLLOW} ${SERVICE}
fi
