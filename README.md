# Belle House Backend API

**Système de Gestion pour Belle House** - Backend Django REST API pour l'écosystème Belle House (entreprise de construction au Niger).

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.14-red.svg)](https://django-rest-framework.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table des Matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Stack Technique](#stack-technique)
- [Installation](#installation)
- [Déploiement Production](#déploiement-production)
- [Documentation API](#documentation-api)
- [Tests](#tests)
- [Scripts Utilitaires](#scripts-utilitaires)

---

## 🏠 Aperçu

Ce backend sert trois frontends distincts :

1. **Site Web Public** - Portfolio, services, blog (HTML/Bootstrap)
2. **Application Mobile (Flutter)** - Portail client pour suivi des projets
3. **Panel Admin** - Gestion interne des projets, factures, leads

### Architecture API

```
/api/
├── auth/           # Authentification JWT (register, login, password)
├── portfolio/      # Portfolio public (maquettes, réalisations)
├── services/       # Services Belle House
├── blog/           # Articles de blog
├── testimonials/   # Témoignages clients
├── partners/       # Partenaires
├── contact/        # Formulaire de contact
├── build-for-me/   # Leads construction
├── app/            # Endpoints application mobile (authentifié)
│   ├── profile/    # Profil client
│   ├── my-projects/# Projets du client
│   └── promotions/ # Promotions app
└── admin-api/      # Endpoints administration (staff only)
    ├── clients/    # Gestion clients
    ├── projects/   # Gestion projets
    ├── invoices/   # Facturation
    └── leads/      # Gestion leads
```

---

## ✨ Fonctionnalités

- **Authentification JWT** avec refresh tokens et blacklist
- **Soft Delete** sur tous les modèles
- **Audit Trail** complet (created_by, updated_by, deleted_by)
- **Push Notifications** via Firebase Cloud Messaging
- **Compression d'images** automatique (Pillow)
- **Numérotation automatique** des factures (BH/ANNÉE/NUMÉRO)
- **Snapshot client** sur les factures
- **API Documentation** Swagger/OpenAPI

---

## 🛠 Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Framework | Django 4.2 + Django REST Framework |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | djangorestframework-simplejwt |
| Push | firebase-admin |
| CORS | django-cors-headers |
| Audit | django-auditlog |
| Docs | drf-spectacular |
| Server | Gunicorn + Nginx |
| Container | Docker + Docker Compose |

---

## 🚀 Installation

### Prérequis

- Python 3.12+
- pip
- Git
- Docker & Docker Compose (pour production)

### Installation Locale (Développement)

```bash
# Cloner le repo
git clone https://github.com/bellehouse/backend.git
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env

# Appliquer les migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

L'API est disponible sur `http://localhost:8000/api/docs/`

### Installation avec Docker (Développement)

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Lancer avec docker-compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Créer un superuser
docker-compose exec web python manage.py createsuperuser
```

---

## 🌐 Déploiement Production

### Prérequis Serveur (OVHCloud VPS)

- Ubuntu 22.04 LTS
- Docker & Docker Compose
- Domaine configuré (ex: api.bellehouse.ne)

### Étapes de Déploiement

1. **Connexion au serveur**
   ```bash
   ssh user@your-server-ip
   ```

2. **Cloner le repository**
   ```bash
   git clone https://github.com/bellehouse/backend.git
   cd backend
   ```

3. **Configurer l'environnement**
   ```bash
   cp .env.prod.example .env
   nano .env  # Éditer avec vos valeurs
   ```

4. **Configurer Firebase (notifications push)**
   ```bash
   # Placer le fichier de credentials Firebase
   nano firebase-credentials.json
   ```

5. **Initialiser SSL avec Let's Encrypt**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/init_ssl.sh api.bellehouse.ne admin@bellehouse.ne
   ```

6. **Déployer l'application**
   ```bash
   ./scripts/deploy.sh --build
   ```

7. **Créer un superuser**
   ```bash
   ./scripts/create_superuser.sh
   ```

### Mise à Jour Production

```bash
./scripts/deploy.sh
```

### Backups Base de Données

```bash
# Backup manuel
./scripts/backup_db.sh

# Restauration
./scripts/restore_db.sh backups/bellehouse_backup_YYYYMMDD_HHMMSS.sql.gz

# Backup automatique (cron)
# Ajouter dans crontab -e :
0 2 * * * /home/user/backend/scripts/backup_db.sh >> /var/log/bellehouse_backup.log 2>&1
```

---

## 📖 Documentation API

- **Swagger UI**: `https://api.bellehouse.ne/api/docs/`
- **ReDoc**: `https://api.bellehouse.ne/api/redoc/`
- **OpenAPI Schema**: `https://api.bellehouse.ne/api/schema/`

### Authentification

Toutes les requêtes authentifiées nécessitent un header :
```
Authorization: Bearer <access_token>
```

Obtenir un token :
```bash
curl -X POST https://api.bellehouse.ne/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=. --cov-report=html

# Tests spécifiques
pytest tests/test_auth.py -v
pytest tests/test_billing.py -v
```

### Structure des Tests

```
tests/
├── conftest.py         # Fixtures pytest
├── test_auth.py        # Tests authentification (18 tests)
├── test_marketing.py   # Tests API publique (13 tests)
├── test_clients.py     # Tests application mobile (12 tests)
├── test_billing.py     # Tests facturation (11 tests)
└── test_notifications.py # Tests notifications (10 tests)
```

---

## 🔧 Scripts Utilitaires

| Script | Description |
|--------|-------------|
| `scripts/deploy.sh` | Déploiement automatisé |
| `scripts/backup_db.sh` | Backup base de données |
| `scripts/restore_db.sh` | Restauration backup |
| `scripts/init_ssl.sh` | Configuration SSL Let's Encrypt |
| `scripts/create_superuser.sh` | Création superuser |
| `scripts/logs.sh` | Affichage logs Docker |

---

## 📁 Structure du Projet

```
bellehouse-backend/
├── config/             # Configuration Django
│   ├── settings.py     # Paramètres
│   ├── urls.py         # URLs principales
│   └── admin_urls.py   # URLs admin API
├── core/               # App authentification
│   ├── models.py       # BaseModel, User
│   ├── views.py        # Auth views
│   └── notifications.py# Service notifications
├── marketing/          # App contenu public
│   ├── models.py       # Portfolio, Service, Blog...
│   └── views.py        # API publique
├── clients/            # App mobile client
│   ├── models.py       # ClientProfile, ActiveProject
│   └── views.py        # Endpoints mobile
├── billing/            # App facturation
│   ├── models.py       # Invoice, InvoiceItem
│   └── views.py        # Admin billing
├── leads/              # App leads/contacts
├── templates/          # Templates email
├── tests/              # Tests pytest
├── scripts/            # Scripts déploiement
├── nginx/              # Configuration Nginx
├── docker-compose.yml  # Docker Compose
├── Dockerfile          # Image production
└── requirements.txt    # Dépendances Python
```

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Contact

**Belle House SARL**  
Niamey, Niger  
📧 contact@bellehouse.ne  
🌐 https://bellehouse.ne
