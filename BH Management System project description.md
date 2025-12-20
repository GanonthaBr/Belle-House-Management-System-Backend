# Backend Implementation Specification: Belle House Ecosystem

**Version:** 2.0  
**Date:** December 19, 2025  
**Role:** Backend Developer (Django)  
**Status:** Final Specification (Ready for Implementation)

---

## 1. Project Overview

The goal is to build a centralized backend API using **Django** and **Django REST Framework (DRF)**. This system will serve three distinct frontends:

1. **Public Website:** A static HTML/Bootstrap site (consumes public API for Portfolio/Services).
2. **Mobile App (Flutter):** A client portal for monitoring construction progress and billing.
3. **Admin Panel:** An internal tool for staff to manage projects, leads, and billing.

---

## 2. Technical Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| **Framework** | Django 4.x + Django REST Framework | Core backend |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Switch via environment variable |
| **Authentication** | `djangorestframework-simplejwt` | JWT for both clients and admin staff |
| **Media Storage** | Local filesystem (dev) / Cloudinary (prod) | Image compression with Pillow |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | Via `fcm-django` or `firebase-admin` |
| **Email** | SMTP (Gmail for dev) / SendGrid (prod) | For password reset & notifications |
| **CORS** | `django-cors-headers` | Whitelist frontend domains |
| **Audit Logging** | `django-auditlog` or `django-simple-history` | Track all data changes |
| **Deployment** | Docker + Docker Compose | On OVHCloud VPS |
| **Web Server** | Nginx + Gunicorn | Reverse proxy + WSGI |

### Key Python Packages
```
django>=4.2
djangorestframework>=3.14
djangorestframework-simplejwt
django-cors-headers
django-filter
Pillow
python-decouple
fcm-django
django-auditlog
```

---

## 3. Critical Concept: Two Types of "Projects"

⚠️ **IMPORTANT: Do NOT confuse these two concepts. They are completely independent.**

| Model | Name | Purpose | Client Link | Where Used |
|-------|------|---------|-------------|------------|
| `PortfolioItem` | Marketing Portfolio | Designs/maquettes and completed works uploaded for **marketing purposes only** | ❌ NO | Public website |
| `ActiveProject` | Client Project | Real contracted work being tracked for a **specific paying client** | ✅ YES | Mobile app |

### PortfolioItem (Marketing Content)
- Uploaded manually by admin for the **public website**
- Has two categories:
  - `PROJECT` = Design maquettes (not built yet, for showcasing capabilities)
  - `REALIZATION` = Completed works (built and finished, for showcasing portfolio)
- **Never linked to a client** — purely for marketing
- Visible to the public without authentication

### ActiveProject (Client Contract)
- Created when Belle House **signs a contract** with a client
- Linked to a `ClientProfile` (the paying customer)
- Tracks progress, updates, and invoices
- **Only visible to the authenticated client** in the mobile app

---

## 4. Database Models (Schema)

### Base Abstract Models (Apply to ALL models)

**`BaseModel`** — All models inherit from this:
```python
class BaseModel(models.Model):
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    # Audit
    created_by = ForeignKey(User, null=True, on_delete=SET_NULL, related_name='+')
    updated_by = ForeignKey(User, null=True, on_delete=SET_NULL, related_name='+')
    
    # Soft Delete
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField(null=True, blank=True)
    deleted_by = ForeignKey(User, null=True, on_delete=SET_NULL, related_name='+')
    
    class Meta:
        abstract = True
```

**Custom Manager** — Filter out soft-deleted records by default:
```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
```

---

### A. Marketing & Website Content (Public)

These models populate the public website. **No client relationship.**

**1. `PortfolioItem`** (Marketing designs and completed works)

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | Verbose: "Nom du Projet" |
| `slug` | SlugField | Unique, for URLs |
| `category` | ChoiceField | `PROJECT` (maquette) or `REALIZATION` (completed) |
| `main_image` | ImageField | Thumbnail |
| `description` | TextField | |
| `area` | CharField | e.g., "405,30 m²" |
| `task` | CharField | e.g., "Conception et Réalisation" |
| `owner` | CharField | e.g., "M. Christophe" (for display only) |
| `contractor` | CharField | Default: "Belle House" |
| `year` | IntegerField | |
| `usage` | CharField | e.g., "Habitation" |
| `district` | CharField | e.g., "Niamey" |
| `city` | CharField | |
| `country` | CharField | |

**2. `PortfolioGalleryImage`**
| Field | Type | Notes |
|-------|------|-------|
| `portfolio_item` | ForeignKey | → `PortfolioItem` |
| `image` | ImageField | Compress on upload |

**3. `PortfolioVideo`**
| Field | Type | Notes |
|-------|------|-------|
| `portfolio_item` | ForeignKey | → `PortfolioItem` |
| `video_url` | URLField | YouTube/Vimeo links |
| `title` | CharField | |

**4. `Service`**
| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | |
| `icon` | ImageField | SVG/PNG |
| `short_description` | TextField | |
| `order` | IntegerField | For sorting |

**5. `Partner`**
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField | |
| `logo` | ImageField | |
| `website` | URLField | |
| `order` | IntegerField | For sorting |

**6. `Testimonial`**
| Field | Type | Notes |
|-------|------|-------|
| `client_name` | CharField | |
| `role` | CharField | e.g., "Propriétaire" |
| `photo` | ImageField | |
| `content` | TextField | |
| `rating` | IntegerField | 1-5 |
| `is_featured` | BooleanField | |

**7. `BlogPost`**
| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | |
| `slug` | SlugField | Unique |
| `thumbnail` | ImageField | |
| `content` | TextField | |
| `published_date` | DateTimeField | |

---

### B. Lead Generation (Public → Private)

**8. `ConstructionLead`** ("Build For Me" Form)

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField | |
| `phone` | CharField | |
| `email` | EmailField | |
| `has_land` | BooleanField | |
| `location_of_land` | CharField | |
| `interested_in` | ForeignKey | → `PortfolioItem` (nullable) — tracks which design attracted them |
| `status` | ChoiceField | `NEW`, `CONTACTED`, `CONVERTED`, `LOST` |

> **Note:** `budget_range` field removed per client decision.

**9. `ContactInquiry`** (Simple Contact Form)

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField | |
| `email` | EmailField | |
| `phone` | CharField | |
| `subject` | CharField | |
| `message` | TextField | |
| `is_read` | BooleanField | |

---

### C. Client Portal (Mobile App) — Authenticated Clients Only

**10. `ClientProfile`**

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOneField | → Django `User` model |
| `phone` | CharField | |
| `address` | CharField | For invoice snapshots |
| `whatsapp_enabled` | BooleanField | Reserved for future use |
| `fcm_token` | CharField | For push notifications |

> **Account Creation:** Admins create accounts only. No self-registration. System sends credentials via email upon creation.

**11. `ActiveProject`** (Client's contracted work — **NOT marketing**)

| Field | Type | Notes |
|-------|------|-------|
| `client` | ForeignKey | → `ClientProfile` (**One client can have MULTIPLE projects**) |
| `project_name` | CharField | |
| `start_date` | DateField | |
| `estimated_completion` | DateField | |
| `progress_percentage` | IntegerField | 0-100 |
| `current_phase` | ChoiceField | Foundation, Elevation, Roofing, Finishing, Handover |
| `total_quote` | DecimalField | |
| `amount_paid` | DecimalField | |

**12. `ProjectUpdate`** (Progress feed for clients)

| Field | Type | Notes |
|-------|------|-------|
| `project` | ForeignKey | → `ActiveProject` |
| `image` | ImageField | Site photo |
| `title` | CharField | |
| `description` | TextField | |
| `posted_at` | DateTimeField | |

> **Trigger:** Creating a `ProjectUpdate` sends push notification to the client.

**13. `AppPromotion`** (Marketing banners in mobile app)

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | |
| `banner_image` | ImageField | |
| `linked_portfolio` | ForeignKey | → `PortfolioItem` (nullable) |
| `external_link` | URLField | Nullable |
| `is_active` | BooleanField | |

---

### D. Billing & Invoicing

**14. `Invoice`**

| Field | Type | Notes |
|-------|------|-------|
| `project` | ForeignKey | → `ActiveProject` |
| `invoice_number` | CharField | **Auto-generated:** `BH/{year}/{auto_increment}` |
| `subject` | CharField | e.g., "Plan et suivie" |
| `status` | ChoiceField | `DRAFT`, `SENT`, `PAID`, `OVERDUE`, `CANCELLED` |
| `issue_date` | DateField | |
| `due_date` | DateField | Payment deadline |
| `tax_percentage` | DecimalField | Default 0.00 |
| `advance_payment` | DecimalField | Default 0.00 |
| `payment_mode` | ChoiceField | `CASH`, `TRANSFER`, `CHECK` |
| `client_name` | CharField | Snapshot — auto-filled from client |
| `client_address` | CharField | Snapshot — auto-filled from client |
| `client_phone` | CharField | Snapshot — auto-filled from client |

**Invoice Number Auto-Generation Logic:**
```python
def generate_invoice_number():
    current_year = datetime.now().year
    last_invoice = Invoice.objects.filter(
        invoice_number__startswith=f"BH/{current_year}/"
    ).order_by('-id').first()
    
    if last_invoice:
        last_num = int(last_invoice.invoice_number.split('/')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"BH/{current_year}/{new_num}"
```

**Computed Properties:**
- `subtotal` → Sum of all invoice items
- `tax_amount` → `subtotal * tax_percentage / 100`
- `total_ttc` → `subtotal + tax_amount`
- `net_to_pay` → `total_ttc - advance_payment`

> **Trigger:** Creating an `Invoice` sends push notification + email to the client.

**15. `InvoiceItem`**

| Field | Type | Notes |
|-------|------|-------|
| `invoice` | ForeignKey | → `Invoice` |
| `description` | TextField | Must allow long descriptions |
| `quantity` | DecimalField | |
| `unit_price` | DecimalField | |

**Computed:** `total_price` → `quantity * unit_price`

---

## 5. Authentication & Authorization

### Authentication Method
- **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`
- Both **mobile app clients** and **admin staff** authenticate via JWT
- Django Admin panel continues using session authentication

### User Roles

| Role | Description | Access |
|------|-------------|--------|
| `Client` | Mobile app users (construction clients) | Own projects, updates, invoices only |
| `Staff` | Admin panel users (Belle House employees) | Full CRUD on all data |

### Token Endpoints
```
POST /api/auth/token/          → Get access + refresh tokens
POST /api/auth/token/refresh/  → Refresh access token
POST /api/auth/password-reset/ → Request password reset email
POST /api/auth/password-reset/confirm/ → Confirm password reset
```

### Account Management
- **No self-registration** — Admins create all client accounts
- When admin creates a client account:
  1. System generates a temporary password
  2. Email is sent to client with credentials
  3. Client must change password on first login (optional but recommended)

---

## 6. API Endpoints

### Public API (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolio/` | List all portfolio items (paginated) |
| GET | `/api/portfolio/{slug}/` | Detail with nested gallery_images and videos |
| GET | `/api/services/` | List services (ordered) |
| GET | `/api/partners/` | List partners (ordered) |
| GET | `/api/testimonials/` | List featured testimonials |
| GET | `/api/blog/` | List blog posts (paginated) |
| GET | `/api/blog/{slug}/` | Blog post detail |
| POST | `/api/build-for-me/` | Create ConstructionLead |
| POST | `/api/contact/` | Create ContactInquiry |

### Mobile App API (JWT Auth Required — Client Role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/app/profile/` | Get client's profile |
| PUT | `/api/app/profile/` | Update profile (phone, fcm_token) |
| GET | `/api/app/my-projects/` | List all client's ActiveProjects |
| GET | `/api/app/my-projects/{id}/` | Project detail with nested updates & invoices |
| GET | `/api/app/my-projects/{id}/updates/` | List project updates |
| GET | `/api/app/my-projects/{id}/invoices/` | List project invoices |
| GET | `/api/app/invoices/{id}/` | Invoice detail with items |
| GET | `/api/app/promotions/` | List active AppPromotion items |

### Admin API (JWT Auth Required — Staff Role)

Full CRUD endpoints for all models. Examples:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/admin/clients/` | List/Create clients |
| GET/PUT/DELETE | `/api/admin/clients/{id}/` | Client detail |
| GET/POST | `/api/admin/projects/` | List/Create ActiveProjects |
| GET/PUT/DELETE | `/api/admin/projects/{id}/` | Project detail |
| POST | `/api/admin/projects/{id}/updates/` | Add project update (triggers notification) |
| GET/POST | `/api/admin/invoices/` | List/Create invoices (triggers notification) |
| GET/PUT/DELETE | `/api/admin/invoices/{id}/` | Invoice detail |
| ... | `/api/admin/portfolio/` | Portfolio CRUD |
| ... | `/api/admin/leads/` | Leads management |
| ... | `/api/admin/inquiries/` | Contact inquiries |

---

## 7. Pagination

All list endpoints use **PageNumberPagination**:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

Response format:
```json
{
    "count": 100,
    "next": "http://api.example.com/items/?page=2",
    "previous": null,
    "results": [...]
}
```

---

## 8. Notifications System

### Push Notifications (Firebase Cloud Messaging)

**Triggers:**

| Event | Recipient | Message |
|-------|-----------|---------|
| Client account created | Client | "Welcome to Belle House! Your account has been created." |
| ProjectUpdate created | Project's client | "New update on {project_name}: {update_title}" |
| Invoice created | Project's client | "New invoice #{invoice_number} for {project_name}" |

**Implementation:**
- Store `fcm_token` in `ClientProfile`
- Use Django signals (`post_save`) to trigger notifications
- Use `fcm-django` or `firebase-admin` SDK

### Email Notifications

| Event | Recipient | Content |
|-------|-----------|---------|
| Client account created | Client | Welcome email with credentials |
| Password reset requested | Client | Reset link (valid 24h) |
| Invoice created | Client | Invoice summary + PDF attachment (optional) |

---

## 9. Soft Delete & Audit Trail

### Soft Delete
- All models have `is_deleted`, `deleted_at`, `deleted_by` fields
- Default manager filters out deleted records
- Admin can view/restore deleted records via special endpoint or Django Admin
- **Force delete** available for permanent removal (admin only)

### Audit Trail
- All models track `created_at`, `updated_at`, `created_by`, `updated_by`
- Use `django-auditlog` for detailed change history:
  - What changed
  - Old value → New value
  - Who made the change
  - When

---

## 10. Admin Panel Requirements

The Django Admin must be customized for usability by non-technical staff.

1. **Portfolio Page:** 
   - Use `TabularInline` for Gallery Images and Videos
   - Upload multiple items on the same screen

2. **Client Management:**
   - Action button to create account and send credentials
   - Show related projects inline

3. **ActiveProject Page:**
   - Show progress bar visualization
   - Inline ProjectUpdates
   - Link to related invoices

4. **Invoice Page:**
   - `TabularInline` for InvoiceItems
   - Show calculated fields (Total TTC, Net à Payer) in list view
   - Auto-fill client snapshot on save
   - Auto-generate invoice number on save

5. **Leads/Inquiries:**
   - Mark as read/unread
   - Filter by status
   - Export to CSV

---

## 11. Environment Configuration

### Required Environment Variables

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (use SQLite for dev, PostgreSQL for prod)
DATABASE_URL=postgres://user:pass@host:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://bellehouse.ne

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Firebase (path to credentials JSON)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Media Storage (Cloudinary for prod)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 12. Docker Deployment (OVHCloud VPS)

### Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OVHCloud VPS                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────────┐    ┌────────────────┐  │
│  │  Nginx  │───▶│   Gunicorn  │───▶│  Django App    │  │
│  │  :80    │    │   :8000     │    │  (API)         │  │
│  │  :443   │    └─────────────┘    └────────────────┘  │
│  └─────────┘                              │            │
│       │                                   ▼            │
│       │                           ┌────────────────┐   │
│       │                           │  PostgreSQL    │   │
│       │                           │  :5432         │   │
│       ▼                           └────────────────┘   │
│  ┌─────────────┐                                       │
│  │   Static    │                                       │
│  │   /media    │                                       │
│  └─────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

### Docker Files to Create

**1. `Dockerfile`**
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

**2. `docker-compose.yml`** (Production)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: .
    restart: always
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    command: gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # For HTTPS certificates
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

**3. `docker-compose.dev.yml`** (Development)
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    env_file:
      - .env.dev
    command: python manage.py runserver 0.0.0.0:8000
```

**4. `nginx/nginx.conf`**
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;  # Replace with actual domain

        client_max_body_size 10M;  # For image uploads

        location /static/ {
            alias /app/staticfiles/;
        }

        location /media/ {
            alias /app/media/;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Deployment Commands

```bash
# First deployment
ssh user@your-vps-ip
git clone <repo-url>
cd system_de_gestion_belle_house_backend
cp .env.example .env  # Edit with production values
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Updates
git pull
docker-compose up -d --build
docker-compose exec web python manage.py migrate

# View logs
docker-compose logs -f web

# Database backup
docker-compose exec db pg_dump -U $DB_USER $DB_NAME > backup.sql
```

---

## 13. External Services Setup

### Required Before Production

| Service | Purpose | Setup Time | Free Tier |
|---------|---------|------------|-----------|
| **PostgreSQL** | Production database | Included in Docker | N/A (self-hosted) |
| **Firebase** | Push notifications | 15 min | Yes (generous limits) |
| **Email SMTP** | Transactional emails | 5 min | Gmail: 500/day |
| **Cloudinary** | Image storage/CDN | 10 min | 25GB storage |

### Skipped (Future Enhancement)
- WhatsApp Business API (requires payment)
- SMS Gateway (not required)
- Payment Gateway (invoices tracked, not paid online)
- SSL/HTTPS (use Let's Encrypt + Certbot on VPS)

---

## 14. Implementation Checklist

### Phase 1: Core Setup ✅
- [x] Initialize Django project with proper structure
- [x] Configure settings (dev/prod split)
- [x] Set up `.env` configuration
- [x] Create base abstract models (soft delete, audit)
- [x] Configure JWT authentication
- [x] Set up CORS

### Phase 2: Models & Migrations ✅
- [x] Implement all models (Section 4)
- [x] Create and run migrations
- [x] Set up custom managers for soft delete

### Phase 3: API Development ✅
- [x] Create serializers (nested for related objects)
- [x] Implement public API endpoints
- [x] Implement mobile app API endpoints
- [x] Implement admin API endpoints
- [x] Add pagination
- [x] Authentication endpoints (register, login, logout, password reset)
- [x] Swagger/OpenAPI documentation (`/api/docs/`)

### Phase 4: Business Logic ✅
- [x] Invoice auto-numbering (`BH/2025/1` format)
- [x] Client snapshot on invoice save
- [x] Image compression on upload (Pillow)
- [x] Lead conversion signals (optional auto-convert)

### Phase 5: Notifications ✅
- [x] Integrate Firebase FCM (push notifications)
- [x] Set up email templates (welcome, password reset, invoice, project update)
- [x] Implement signal handlers for triggers (project update, new invoice)
- [x] FCM token update endpoint (`/api/app/fcm-token/`)

### Phase 6: Admin Panel ✅
- [x] Customize Django Admin
- [x] Add inlines for related models
- [x] Add list filters and search
- [x] Add custom actions (mark invoices as sent/paid/overdue)
- [x] Autocomplete fields for ForeignKey relations

### Phase 7: Testing & Documentation
- [ ] Write API tests
- [ ] Test notification flows
- [x] Generate API documentation (Swagger/OpenAPI)

### Phase 8: Docker & Deployment
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml (prod)
- [ ] Create docker-compose.dev.yml (dev)
- [ ] Create nginx.conf
- [ ] Create .env.example template
- [ ] Test local Docker build
- [ ] Deploy to OVHCloud VPS
- [ ] Set up SSL with Let's Encrypt
- [X] Configure domain DNS

---

**End of Document**