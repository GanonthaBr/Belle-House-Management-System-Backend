# 🔧 DNS Configuration Fix for api2.bellehouseniger.com

Since your domain was reinitialized at the registrar, you need to reconfigure DNS records.

## Step 1: Configure DNS at Your Domain Registrar

### Required DNS Records:

**A Record (Required)**
```
Type: A
Name: api2
Value/Points to: 51.91.159.155
TTL: 3600 (or Auto)
```

**Optional but Recommended:**
```
Type: A
Name: @
Value/Points to: 51.91.159.155
TTL: 3600

Type: A
Name: www
Value/Points to: 51.91.159.155
TTL: 3600
```

### How to Add These Records:

1. Login to your domain registrar (where you bought bellehouseniger.com)
2. Find DNS Management / DNS Zone / DNS Settings
3. Add the A record above
4. Save changes

⏰ **DNS propagation takes 5-60 minutes** (sometimes up to 24 hours)

---

## Step 2: Verify DNS Configuration

### From Windows PowerShell:

```powershell
# Check if DNS is pointing to your VPS
nslookup api2.bellehouseniger.com

# Expected output should show: 51.91.159.155
```

### Or use online tool:
Visit: https://dnschecker.org/#A/api2.bellehouseniger.com

---

## Step 3: Check VPS is Running (SSH to VPS)

```bash
# Connect to VPS
ssh root@51.91.159.155

# Check Docker containers
docker ps

# You should see:
# - bellehouse_web
# - bellehouse_nginx  
# - bellehouse_db
# - bellehouse_certbot

# If containers are not running:
cd /root/bellehouse-backend  # or wherever deployed
docker-compose up -d

# Check nginx is listening
netstat -tulpn | grep :80
netstat -tulpn | grep :443
```

---

## Step 4: Regenerate SSL Certificate

Since the domain was reinitialized, SSL certificate may be invalid:

```bash
# SSH to VPS first
ssh root@51.91.159.155

# Go to project directory
cd /root/bellehouse-backend  # Adjust if different

# Stop current setup
docker-compose down

# Remove old certificates
rm -rf certbot/conf/live/api2.bellehouseniger.com
rm -rf certbot/conf/archive/api2.bellehouseniger.com
rm -rf certbot/conf/renewal/api2.bellehouseniger.com.conf

# Make sure DNS is pointing to VPS first (wait 10-15 mins after DNS setup)
# Then run SSL setup script:
chmod +x scripts/init_ssl.sh
./scripts/init_ssl.sh api2.bellehouseniger.com your-email@example.com

# If script fails, try manual approach:
docker-compose up -d nginx

docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d api2.bellehouseniger.com

# Restart all services
docker-compose down
docker-compose up -d
```

---

## Step 5: Verify Everything Works

### Test HTTP (should redirect to HTTPS):
```
http://api2.bellehouseniger.com
```

### Test HTTPS:
```
https://api2.bellehouseniger.com
https://api2.bellehouseniger.com/admin
https://api2.bellehouseniger.com/api/v1/
```

### Check from PowerShell:
```powershell
# Test if server responds
curl.exe https://api2.bellehouseniger.com

# Test admin
curl.exe https://api2.bellehouseniger.com/admin/
```

---

## Troubleshooting

### Problem: "Site can't be reached" or "DNS_PROBE_FINISHED_NXDOMAIN"
**Cause:** DNS not configured or not propagated yet
**Solution:** 
- Double-check DNS A record at registrar
- Wait 15-30 minutes for propagation
- Clear browser cache or try incognito mode

### Problem: "Connection timed out"
**Cause:** VPS firewall blocking ports or containers not running
**Solution:**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Check containers
docker-compose ps
docker-compose logs nginx
```

### Problem: "ERR_SSL_VERSION_OR_CIPHER_MISMATCH" or SSL error
**Cause:** SSL certificate not generated or invalid
**Solution:** Follow Step 4 to regenerate SSL certificate

### Problem: "502 Bad Gateway"
**Cause:** Nginx can't reach Django backend
**Solution:**
```bash
# Check web container
docker-compose logs web

# Restart services
docker-compose restart
```

---

## Quick Checklist

- [ ] DNS A record created at registrar (api2 → 51.91.159.155)
- [ ] DNS propagated (test with nslookup)
- [ ] VPS Docker containers running (docker ps)
- [ ] Ports 80 and 443 open on firewall
- [ ] SSL certificate generated
- [ ] Site accessible via HTTPS

---

## Your VPS IP Address
**51.91.159.155**

## Your Domain
**api2.bellehouseniger.com**

Make sure these match in your DNS settings!
