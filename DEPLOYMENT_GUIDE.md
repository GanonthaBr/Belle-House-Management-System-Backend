# =============================================================================
# 🚀 GUIDE COMPLET DE DÉPLOIEMENT - Belle House Backend
# =============================================================================
# De zéro au projet en production sur OVHCloud VPS avec GitHub CI/CD
# =============================================================================

## TABLE DES MATIÈRES

1. [Prérequis](#1-prérequis)
2. [Préparation du Repository GitHub](#2-préparation-du-repository-github)
3. [Configuration du VPS OVHCloud](#3-configuration-du-vps-ovhcloud)
4. [Installation des dépendances serveur](#4-installation-des-dépendances-serveur)
5. [Configuration du domaine DNS](#5-configuration-du-domaine-dns)
6. [Déploiement initial](#6-déploiement-initial)
7. [Configuration SSL (HTTPS)](#7-configuration-ssl-https)
8. [GitHub Actions CI/CD](#8-github-actions-cicd)
9. [Webhook pour auto-déploiement](#9-webhook-pour-auto-déploiement)
10. [Backups automatiques](#10-backups-automatiques)
11. [Monitoring et maintenance](#11-monitoring-et-maintenance)
12. [Dépannage](#12-dépannage)

---

## 1. PRÉREQUIS

### Ce dont vous avez besoin :
- [ ] VPS OVHCloud (Ubuntu 22.04 recommandé)
- [ ] Compte GitHub
- [ ] Domaine (optionnel mais recommandé)
- [ ] Compte Gmail (pour les emails) avec App Password
- [ ] Compte Firebase (pour les notifications push) - optionnel

### Informations à préparer :
- IP de votre VPS : `_______________`
- Mot de passe root VPS : `_______________`
- Nom de domaine : `_______________`
- Email admin : `_______________`

---

## 2. PRÉPARATION DU REPOSITORY GITHUB

### 2.1 Créer le repository sur GitHub

1. Allez sur https://github.com/new
2. Nom du repo : `bellehouse-backend`
3. Visibilité : Private (recommandé)
4. Ne pas initialiser avec README (on va push notre code)

### 2.2 Push du code local vers GitHub

Sur votre PC Windows (PowerShell) :

```powershell
cd "C:\Users\bgano\Desktop\Belle House\system_de_gestion_belle_house_backend"

# Initialiser git si pas déjà fait
git init

# Configurer git
git config user.name "Votre Nom"
git config user.email "votre-email@example.com"

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - Belle House Backend"

# Ajouter le remote GitHub
git remote add origin https://github.com/VOTRE-USERNAME/bellehouse-backend.git

# Push vers GitHub
git branch -M main
git push -u origin main
```

### 2.3 Créer un Personal Access Token GitHub

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. Nom : `bellehouse-deploy`
4. Expiration : 90 days ou No expiration
5. Scopes : cocher `repo` (full control)
6. Copier le token : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

⚠️ **SAUVEGARDEZ CE TOKEN** - Vous ne pourrez plus le voir !

---

## 3. CONFIGURATION DU VPS OVHCLOUD

### 3.1 Première connexion SSH

```bash
# Depuis PowerShell sur Windows
ssh root@VOTRE_IP_VPS
```

Entrez le mot de passe reçu par email d'OVHCloud.

### 3.2 Sécurisation initiale

```bash
# Mettre à jour le système
apt update && apt upgrade -y

# Créer un utilisateur non-root
adduser deploy
# Entrez un mot de passe sécurisé

# Ajouter aux sudoers
usermod -aG sudo deploy

# Configurer SSH pour cet utilisateur
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
```

### 3.3 Configuration SSH (optionnel mais recommandé)

```bash
# Éditer la config SSH
nano /etc/ssh/sshd_config

# Modifier ces lignes :
# PermitRootLogin no          # Désactiver login root (après test avec deploy)
# PasswordAuthentication yes   # Garder yes si pas de clé SSH

# Redémarrer SSH
systemctl restart sshd
```

### 3.4 Configuration du firewall

```bash
# Installer et configurer UFW
apt install -y ufw

# Règles de base
ufw default deny incoming
ufw default allow outgoing

# Autoriser SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Activer le firewall
ufw enable

# Vérifier
ufw status
```

---

## 4. INSTALLATION DES DÉPENDANCES SERVEUR

### 4.1 Installer Docker

```bash
# Installer les prérequis
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Ajouter la clé GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajouter le repository Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Ajouter l'utilisateur deploy au groupe docker
usermod -aG docker deploy

# Vérifier l'installation
docker --version
docker compose version
```

### 4.2 Installer les outils nécessaires

```bash
apt install -y git nano htop ncdu
```

### 4.3 Se connecter en tant que deploy

```bash
# Sortir de root
exit

# Se reconnecter avec l'utilisateur deploy
ssh deploy@VOTRE_IP_VPS
```

---

## 5. CONFIGURATION DU DOMAINE DNS

### 5.1 Sans domaine (accès par IP)

Si vous n'avez pas de domaine, vous pouvez accéder à l'API via :
- `http://VOTRE_IP_VPS/api/docs/`

### 5.2 Avec domaine OVHCloud

1. Connectez-vous à votre [Manager OVHCloud](https://www.ovh.com/manager/)
2. Web Cloud → Noms de domaine → Votre domaine → Zone DNS

Ajoutez ces enregistrements :

| Type | Sous-domaine | Cible | TTL |
|------|--------------|-------|-----|
| A | @ | VOTRE_IP_VPS | 3600 |
| A | api | VOTRE_IP_VPS | 3600 |
| A | www | VOTRE_IP_VPS | 3600 |

### 5.3 Avec autre registrar (Namecheap, GoDaddy, etc.)

Dans les DNS Settings, ajoutez :
- Type A : `@` → `VOTRE_IP_VPS`
- Type A : `api` → `VOTRE_IP_VPS`

⚠️ **Attendez 5-30 minutes** pour la propagation DNS.

Vérifier la propagation :
```bash
nslookup api.votre-domaine.com
```

---

## 6. DÉPLOIEMENT INITIAL

### 6.1 Cloner le projet

```bash
# Se connecter en tant que deploy
ssh deploy@VOTRE_IP_VPS

# Créer le dossier d'applications
sudo mkdir -p /var/www
sudo chown deploy:deploy /var/www
cd /var/www

# Cloner depuis GitHub (utilisez votre token)
git clone https://VOTRE_TOKEN@github.com/VOTRE-USERNAME/bellehouse-backend.git
cd bellehouse-backend
```

### 6.2 Configurer l'environnement

```bash
# Copier le template
cp .env.prod.example .env

# Générer une clé secrète
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
# Copiez le résultat

# Éditer le fichier .env
nano .env
```

**Contenu du .env à personnaliser :**

```env
# =============================================================================
# PRODUCTION ENVIRONMENT - Belle House Backend
# =============================================================================

# Django
SECRET_KEY=COLLEZ_LA_CLE_GENEREE_ICI
DEBUG=False
ALLOWED_HOSTS=api.votre-domaine.com,votre-domaine.com,VOTRE_IP_VPS

# Database
POSTGRES_USER=bellehouse
POSTGRES_PASSWORD=MotDePasseTresSecurise123!
POSTGRES_DB=bellehouse_db

# CORS (vos frontends)
CORS_ALLOWED_ORIGINS=https://votre-domaine.com,https://app.votre-domaine.com

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password-16-caracteres
DEFAULT_FROM_EMAIL=Belle House <noreply@votre-domaine.com>

# Firebase (optionnel - pour notifications push)
# FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

# Security
SECURE_SSL_REDIRECT=False
```

### 6.3 Configurer Gmail App Password

1. Allez sur https://myaccount.google.com/security
2. Activez la **Validation en 2 étapes** si pas fait
3. Retournez dans Security → App passwords
4. Créez un App password pour "Mail" sur "Other (Custom name)"
5. Nom : `bellehouse-backend`
6. Copiez le mot de passe de 16 caractères (sans espaces)
7. Collez-le dans `EMAIL_HOST_PASSWORD` du .env

### 6.4 Configurer Nginx pour HTTP (sans SSL d'abord)

```bash
# Créer la configuration Nginx simplifiée
cat > nginx/conf.d/api.conf << 'EOF'
upstream django {
    server web:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api2.bellehouseniger.com bellehouseniger.com 51.91.159.155;

    client_max_body_size 50M;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
```

⚠️ **Remplacez** `votre-domaine.com` et `VOTRE_IP_VPS` par vos vraies valeurs !

### 6.5 Préparer les dossiers

```bash
# Créer les dossiers nécessaires
mkdir -p backups certbot/conf certbot/www

# Rendre les scripts exécutables
chmod +x scripts/*.sh
```

### 6.6 Lancer le premier déploiement

```bash
# Build et démarrage des containers
docker compose up -d --build

# Attendre que les containers démarrent
sleep 15

# Vérifier le statut
docker compose ps

# Si tout est "Up", continuer...
```

### 6.7 Initialiser la base de données

```bash
# Appliquer les migrations
docker compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker compose exec web python manage.py collectstatic --noinput

# Créer le superuser admin
docker compose exec web python manage.py createsuperuser
# Suivez les instructions (email, username, password)
```

### 6.8 Tester l'accès

Ouvrez dans votre navigateur :
- `http://VOTRE_IP_VPS/api/docs/` → Documentation Swagger
- `http://VOTRE_IP_VPS/admin/` → Admin Django

Si ça marche, passez au SSL !

---

## 7. CONFIGURATION SSL (HTTPS)

### 7.1 Obtenir le certificat Let's Encrypt

```bash
# Assurez-vous que le DNS est propagé
nslookup api.votre-domaine.com

# Obtenir le certificat
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email votre-email@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d api.votre-domaine.com
```

### 7.2 Mettre à jour Nginx avec SSL

```bash
cat > nginx/conf.d/api.conf << 'EOF'
upstream django {
    server web:8000;
    keepalive 32;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.votre-domaine.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name api.votre-domaine.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/api.votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.votre-domaine.com/privkey.pem;

    # SSL Configuration
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    client_max_body_size 50M;

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
```

### 7.3 Activer HTTPS dans Django

```bash
# Éditer .env
nano .env

# Modifier cette ligne :
SECURE_SSL_REDIRECT=True
```

### 7.4 Redémarrer les services

```bash
docker compose restart nginx web
```

### 7.5 Tester HTTPS

- `https://api.votre-domaine.com/api/docs/` → Doit fonctionner en HTTPS !

---

## 8. GITHUB ACTIONS CI/CD

### 8.1 Créer le workflow GitHub Actions

Sur votre PC Windows, créez le fichier :

```powershell
mkdir -p ".github/workflows"
```

Créez le fichier `.github/workflows/deploy.yml` :

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django
      
      - name: Run tests
        env:
          SECRET_KEY: test-secret-key-for-ci
          DEBUG: 'True'
        run: |
          pytest tests/ -v --tb=short

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USERNAME }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /var/www/bellehouse-backend
            git pull origin main
            docker compose up -d --build
            docker compose exec -T web python manage.py migrate --noinput
            docker compose exec -T web python manage.py collectstatic --noinput
            echo "Deployment completed at $(date)"
```

### 8.2 Générer une clé SSH pour le déploiement

Sur votre VPS (en tant que deploy) :

```bash
# Générer une nouvelle clé SSH
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy -N ""

# Ajouter la clé publique aux authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys

# Afficher la clé privée (à copier)
cat ~/.ssh/github_deploy
```

Copiez TOUT le contenu (de `-----BEGIN` à `-----END`).

### 8.3 Configurer les secrets GitHub

1. GitHub → Votre repo → Settings → Secrets and variables → Actions
2. Cliquez "New repository secret"

Ajoutez ces 3 secrets :

| Nom | Valeur |
|-----|--------|
| `VPS_HOST` | `VOTRE_IP_VPS` |
| `VPS_USERNAME` | `deploy` |
| `VPS_SSH_KEY` | Collez la clé privée complète |

### 8.4 Push et test du CI/CD

```powershell
cd "C:\Users\bgano\Desktop\Belle House\system_de_gestion_belle_house_backend"

# Ajouter les fichiers GitHub Actions
git add .github/
git commit -m "Add GitHub Actions CI/CD"
git push origin main
```

Allez sur GitHub → Actions pour voir le déploiement en cours !

---

## 9. WEBHOOK POUR AUTO-DÉPLOIEMENT (Alternative)

Si vous préférez un webhook plutôt que SSH :

### 9.1 Créer un script de déploiement webhook

Sur le VPS :

```bash
cat > /var/www/bellehouse-backend/scripts/webhook_deploy.sh << 'EOF'
#!/bin/bash
cd /var/www/bellehouse-backend
git pull origin main
docker compose up -d --build
docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py collectstatic --noinput
echo "Deployed at $(date)" >> /var/log/bellehouse_deploy.log
EOF

chmod +x /var/www/bellehouse-backend/scripts/webhook_deploy.sh
```

### 9.2 Installer webhook listener

```bash
# Installer webhook
sudo apt install -y webhook

# Créer la config webhook
cat > /etc/webhook.conf << 'EOF'
[
  {
    "id": "bellehouse-deploy",
    "execute-command": "/var/www/bellehouse-backend/scripts/webhook_deploy.sh",
    "command-working-directory": "/var/www/bellehouse-backend",
    "trigger-rule": {
      "match": {
        "type": "value",
        "value": "VOTRE_SECRET_WEBHOOK",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature"
        }
      }
    }
  }
]
EOF

# Démarrer webhook
webhook -hooks /etc/webhook.conf -verbose
```

---

## 10. BACKUPS AUTOMATIQUES

### 10.1 Configurer le cron pour backups

```bash
# Éditer le crontab
crontab -e

# Ajouter ces lignes :
# Backup quotidien à 2h du matin
0 2 * * * /var/www/bellehouse-backend/scripts/backup_db.sh >> /var/log/bellehouse_backup.log 2>&1

# Renouvellement SSL tous les mois
0 3 1 * * docker compose -f /var/www/bellehouse-backend/docker-compose.yml run --rm certbot renew
```

### 10.2 Backup vers stockage externe (optionnel)

```bash
# Installer rclone pour backup vers cloud
curl https://rclone.org/install.sh | sudo bash

# Configurer (suivre les instructions)
rclone config

# Ajouter au script de backup
echo 'rclone copy /var/www/bellehouse-backend/backups remote:bellehouse-backups' >> /var/www/bellehouse-backend/scripts/backup_db.sh
```

---

## 11. MONITORING ET MAINTENANCE

### 11.1 Commandes utiles

```bash
# Voir les logs en temps réel
docker compose logs -f web

# Voir l'utilisation des ressources
docker stats

# Espace disque
df -h
ncdu /var/www

# Redémarrer tout
docker compose restart

# Arrêter tout
docker compose down

# Reconstruire après modification
docker compose up -d --build
```

### 11.2 Configurer les alertes (optionnel)

Utilisez UptimeRobot (gratuit) :
1. https://uptimerobot.com
2. Add New Monitor
3. URL : `https://api.votre-domaine.com/api/docs/`
4. Alert : votre email

---

## 12. DÉPANNAGE

### Problème : Les containers ne démarrent pas

```bash
# Voir les logs détaillés
docker compose logs

# Reconstruire complètement
docker compose down
docker compose up -d --build
```

### Problème : Erreur de migration

```bash
# Entrer dans le container
docker compose exec web bash

# Vérifier les migrations
python manage.py showmigrations

# Forcer les migrations
python manage.py migrate --fake-initial
```

### Problème : 502 Bad Gateway

```bash
# Vérifier que le web container tourne
docker compose ps

# Redémarrer
docker compose restart web nginx
```

### Problème : Certificat SSL expiré

```bash
# Renouveler le certificat
docker compose run --rm certbot renew

# Redémarrer nginx
docker compose restart nginx
```

### Problème : Base de données corrompue

```bash
# Restaurer depuis backup
./scripts/restore_db.sh backups/bellehouse_backup_LATEST.sql.gz
```

---

## ✅ CHECKLIST FINALE

- [ ] VPS configuré et sécurisé
- [ ] Docker et Docker Compose installés
- [ ] DNS configuré et propagé
- [ ] Code déployé depuis GitHub
- [ ] .env configuré avec vraies valeurs
- [ ] Base de données initialisée
- [ ] Superuser créé
- [ ] SSL/HTTPS configuré
- [ ] GitHub Actions CI/CD fonctionnel
- [ ] Backups automatiques configurés
- [ ] API accessible : `https://api.votre-domaine.com/api/docs/`

---

## 🎉 FÉLICITATIONS !

Votre backend Belle House est maintenant en production !

**URLs de votre API :**
- Documentation : `https://api.votre-domaine.com/api/docs/`
- Admin Django : `https://api.votre-domaine.com/admin/`
- API endpoints : `https://api.votre-domaine.com/api/...`

**Pour mettre à jour :**
1. Faites vos modifications localement
2. `git add . && git commit -m "description" && git push`
3. GitHub Actions déploie automatiquement !

