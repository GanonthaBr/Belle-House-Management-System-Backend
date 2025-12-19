#!/bin/bash
# =============================================================================
# Belle House Backend - Initial SSL Setup with Let's Encrypt
# =============================================================================
# Usage: ./scripts/init_ssl.sh your-domain.com your-email@example.com

set -e

# Check arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 api.bellehouse.ne admin@bellehouse.ne"
    exit 1
fi

DOMAIN=$1
EMAIL=$2

echo "========================================="
echo "  SSL Certificate Setup for ${DOMAIN}"
echo "========================================="

# Create directories
mkdir -p certbot/conf certbot/www

# Create temporary nginx config for certificate validation
cat > nginx/conf.d/temp.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'SSL setup in progress...';
        add_header Content-Type text/plain;
    }
}
EOF

# Start nginx with temp config
echo "Starting Nginx for certificate validation..."
docker-compose up -d nginx

# Wait for nginx to start
sleep 5

# Request certificate
echo "Requesting SSL certificate..."
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email ${EMAIL} \
    --agree-tos \
    --no-eff-email \
    -d ${DOMAIN}

# Remove temp config
rm nginx/conf.d/temp.conf

# Update nginx config with correct domain
sed -i "s/api.bellehouse.ne/${DOMAIN}/g" nginx/conf.d/api.conf

# Restart nginx with SSL config
echo "Restarting Nginx with SSL..."
docker-compose restart nginx

echo "========================================="
echo "  SSL Certificate Setup Complete!"
echo "========================================="
echo "Your API is now available at: https://${DOMAIN}"
