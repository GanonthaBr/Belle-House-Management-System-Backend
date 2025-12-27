# 📱 Belle House Mobile App - API Documentation

**Version:** 1.0.0  
**Last Updated:** December 2025  
**API Base URL:** `https://api2.bellehouseniger.com/api`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication-endpoints)
   - [Home/Dashboard](#homedashboard)
   - [Chantier/Site Feed](#chantiersiteфeed)
   - [Finances/Invoices](#financesinvoices)
   - [Profile/Settings](#profilesettings)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

---

## Overview

This API powers the Belle House mobile application, which allows clients to track their construction projects in real-time. The app has **four main sections**, each requiring specific API endpoints:

### 🏠 Home (Dashboard)
Displays the "Control Center" with:
- Project summary & progress
- Current phase information
- Marketing banners/promotions

### 🏗️ Chantier (Site Feed)
Instagram-style feed of:
- Construction photos
- Daily project updates
- Progress notifications

### 💳 Finances (Invoices)
Financial overview:
- List of all invoices (Paid/Pending)
- Detailed invoice receipts
- Payment status tracking

### 👤 Profile (Settings)
User management:
- Profile information
- WhatsApp contact support
- Logout & account management

---

## Authentication

### JWT Token-Based Authentication

All authenticated endpoints require a **Bearer token** in the Authorization header:

```
Authorization: Bearer {access_token}
```

### Token Lifetime
- **Access Token:** 60 minutes
- **Refresh Token:** 7 days
- Tokens automatically rotate on refresh

### Headers Required

All authenticated requests must include:

```http
Content-Type: application/json
Authorization: Bearer {access_token}
```

---

## API Endpoints

### Authentication Endpoints

#### 1️⃣ Register
**Create a new client account**

```http
POST /auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "Compte créé avec succès.",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

#### 2️⃣ Login
**Authenticate user with username or email**

```http
POST /auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Alternative (using email):**
```json
{
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (200 OK):**
```json
{
  "message": "Connexion réussie.",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

#### 3️⃣ Refresh Token
**Get a new access token using refresh token**

```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### 4️⃣ Get Current User Profile
**Retrieve authenticated user's details**

```http
GET /auth/me/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

#### 5️⃣ Change Password
**Update user password**

```http
POST /auth/change-password/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "old_password_123",
  "new_password": "new_password_456",
  "confirm_password": "new_password_456"
}
```

**Response (200 OK):**
```json
{
  "message": "Mot de passe modifié avec succès."
}
```

---

### Home/Dashboard

#### 1️⃣ Get Client Profile
**Fetch client's profile information**

```http
GET /app/profile/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+227 91 23 45 67",
  "address": "Niamey, Niger",
  "whatsapp_enabled": true,
  "fcm_token": "dUmMy_tOkEn_123..."
}
```

---

#### 2️⃣ Get My Projects List
**Fetch all projects assigned to the client (Dashboard Summary)**

```http
GET /app/my-projects/
Authorization: Bearer {access_token}
```

**Query Parameters (Optional):**
- `page=1` - Pagination (default page size: 20)

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "project_name": "Villa Christophe",
      "description": "Modern villa with pool",
      "start_date": "2024-01-15",
      "estimated_completion": "2025-06-30",
      "progress_percentage": 65,
      "current_phase": "FINITION",
      "current_phase_display": "Finition",
      "total_quote": 50000000.00,
      "amount_paid": 32500000.00,
      "remaining_amount": 17500000.00,
      "payment_percentage": 65.00,
      "location": "Niamey - Plateau"
    },
    {
      "id": 2,
      "project_name": "Bureau Administratif",
      "description": "Office complex",
      "start_date": "2024-06-01",
      "estimated_completion": "2025-12-31",
      "progress_percentage": 35,
      "current_phase": "ELEVATION",
      "current_phase_display": "Élévation",
      "total_quote": 75000000.00,
      "amount_paid": 26250000.00,
      "remaining_amount": 48750000.00,
      "payment_percentage": 35.00,
      "location": "Maradi"
    }
  ]
}
```

---

#### 3️⃣ Get Active Promotions
**Fetch marketing banners for the app homepage**

```http
GET /app/promotions/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Modern Villa Design",
      "banner_image": "https://api2.bellehouseniger.com/media/promotions/banners/villa_2024.jpg",
      "linked_portfolio": 5,
      "external_link": "",
      "is_active": true,
      "order": 1,
      "created_at": "2025-01-10T14:23:00Z"
    },
    {
      "id": 2,
      "title": "New Year Special Offer",
      "banner_image": "https://api2.bellehouseniger.com/media/promotions/banners/newyear_2025.jpg",
      "linked_portfolio": null,
      "external_link": "https://bellehouseniger.com/special-offer",
      "is_active": true,
      "order": 2,
      "created_at": "2024-12-20T10:15:00Z"
    }
  ]
}
```

---

### Chantier/Site Feed

#### 1️⃣ Get Project Details (with Timeline)
**Fetch detailed project information including all updates**

```http
GET /app/my-projects/{project_id}/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "client": 1,
  "project_name": "Villa Christophe",
  "description": "Modern villa with pool and modern architecture",
  "start_date": "2024-01-15",
  "estimated_completion": "2025-06-30",
  "progress_percentage": 65,
  "current_phase": "FINITION",
  "current_phase_display": "Finition",
  "total_quote": 50000000.00,
  "amount_paid": 32500000.00,
  "remaining_amount": 17500000.00,
  "payment_percentage": 65.00,
  "location": "Niamey - Plateau",
  "created_at": "2024-01-10T08:30:00Z",
  "updated_at": "2025-12-20T15:45:00Z"
}
```

---

#### 2️⃣ Get Project Updates (Instagram-style Feed)
**Fetch all construction updates and progress photos for a project**

```http
GET /app/my-projects/{project_id}/updates/
Authorization: Bearer {access_token}
```

**Query Parameters (Optional):**
- `page=1` - Pagination (default page size: 20)

**Response (200 OK):**
```json
[
  {
    "id": 15,
    "title": "Toiture - Jour 1",
    "description": "Beginning of roof installation. Excellent weather conditions today. Team progress on schedule. Expecting to complete 30% of roofing work by end of this week.",
    "image": "https://api2.bellehouseniger.com/media/projects/updates/roof_phase_day1.jpg",
    "posted_at": "2025-12-20T14:30:00Z"
  },
  {
    "id": 14,
    "title": "Préparation des murs",
    "description": "Walls are now properly prepared for finishing work. Plumbing and electrical installations completed.",
    "image": "https://api2.bellehouseniger.com/media/projects/updates/wall_prep.jpg",
    "posted_at": "2025-12-18T09:15:00Z"
  },
  {
    "id": 13,
    "title": "Pose des portes et fenêtres",
    "description": "All doors and windows installed. Building envelope is now complete.",
    "image": "https://api2.bellehouseniger.com/media/projects/updates/doors_windows.jpg",
    "posted_at": "2025-12-15T16:45:00Z"
  }
]
```

---

### Finances/Invoices

#### 1️⃣ Get Project Invoices
**Fetch all invoices for a specific project**

```http
GET /app/my-projects/{project_id}/invoices/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "invoice_number": "BH/2025/3",
    "subject": "Toiture et finitions",
    "status": "PAID",
    "status_display": "Payé",
    "issue_date": "2025-12-01",
    "due_date": "2025-12-15",
    "total_ttc": 8500000.00,
    "net_to_pay": 0.00,
    "payment_mode": "TRANSFER",
    "payment_mode_display": "Virement",
    "project": 1,
    "project_name": "Villa Christophe",
    "client_name": "John Christophe",
    "created_at": "2025-12-01T10:00:00Z"
  },
  {
    "id": 2,
    "invoice_number": "BH/2025/2",
    "subject": "Élévation et gros oeuvre",
    "status": "PAID",
    "status_display": "Payé",
    "issue_date": "2025-09-01",
    "due_date": "2025-09-30",
    "total_ttc": 12000000.00,
    "net_to_pay": 0.00,
    "payment_mode": "TRANSFER",
    "payment_mode_display": "Virement",
    "project": 1,
    "project_name": "Villa Christophe",
    "client_name": "John Christophe",
    "created_at": "2025-09-01T08:30:00Z"
  },
  {
    "id": 1,
    "invoice_number": "BH/2025/1",
    "subject": "Fondations et préparation",
    "status": "PAID",
    "status_display": "Payé",
    "issue_date": "2025-02-01",
    "due_date": "2025-02-28",
    "total_ttc": 12000000.00,
    "net_to_pay": 0.00,
    "payment_mode": "CASH",
    "payment_mode_display": "Espèces",
    "project": 1,
    "project_name": "Villa Christophe",
    "client_name": "John Christophe",
    "created_at": "2025-02-01T11:20:00Z"
  }
]
```

---

#### 2️⃣ Get Invoice Detail
**Fetch detailed invoice including all line items and breakdown**

```http
GET /app/invoices/{invoice_id}/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "invoice_number": "BH/2025/3",
  "subject": "Toiture et finitions",
  "status": "PAID",
  "status_display": "Payé",
  "issue_date": "2025-12-01",
  "due_date": "2025-12-15",
  "tax_percentage": 18.00,
  "advance_payment": 0.00,
  "payment_mode": "TRANSFER",
  "payment_mode_display": "Virement",
  "client_name": "John Christophe",
  "client_address": "Niamey, Niger",
  "client_phone": "+227 91 23 45 67",
  "subtotal": 7203389.83,
  "tax_amount": 1296610.17,
  "total_ttc": 8500000.00,
  "net_to_pay": 0.00,
  "project": 1,
  "project_name": "Villa Christophe",
  "items": [
    {
      "id": 8,
      "description": "Roofing materials and installation labor",
      "quantity": 405.3,
      "unit_price": 12000.00,
      "total_price": 4863600.00,
      "order": 1
    },
    {
      "id": 9,
      "description": "Interior painting and surface finishes",
      "quantity": 1,
      "unit_price": 2340389.83,
      "total_price": 2340389.83,
      "order": 2
    }
  ],
  "notes": "Final phase payment. Payment due within 15 days of issue.",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-20T14:30:00Z"
}
```

---

### Profile/Settings

#### 1️⃣ Update Profile
**Update client's profile information**

```http
PATCH /app/profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+227 91 23 45 67",
  "address": "Niamey, Niger",
  "fcm_token": "new_fcm_token_xyz123"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+227 91 23 45 67",
  "address": "Niamey, Niger",
  "whatsapp_enabled": true,
  "fcm_token": "new_fcm_token_xyz123"
}
```

---

#### 2️⃣ Update FCM Token (for Push Notifications)
**Register device for push notifications**

```http
POST /app/fcm-token/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "fcm_token": "f-R8k3N9x_dU2P4q..."
}
```

**Response (200 OK):**
```json
{
  "message": "FCM token updated successfully",
  "fcm_token": "f-R8k3N9x_dU2P4q..."
}
```

---

#### 3️⃣ Logout
**Invalidate current access token**

```http
POST /auth/logout/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

## Data Models

### ProjectPhase (Enum)
```
FONDATION          = "Fondation"             (Foundation work)
ELEVATION          = "Élévation"             (Building structure)
PREP_DALLE         = "Préparation dalle"    (Preparation for concrete slab)
COULAGE_DALLE      = "Coulage de la dalle"  (Concrete slab pouring)
DECOFFRAGE_DALLE   = "Décoffrage de la dalle" (Concrete slab removal)
CRÉPISSAGES        = "Crépissages"          (Plastering work)
FINITION           = "Finition"             (Interior finishing)
```

### InvoiceStatus (Enum)
```
DRAFT       = "Brouillon"   (Draft - not yet sent)
SENT        = "Envoyé"      (Sent to client)
PAID        = "Payé"        (Fully paid)
OVERDUE     = "En Retard"   (Past due date)
CANCELLED   = "Annulé"      (Cancelled/void)
```

### PaymentMode (Enum)
```
CASH      = "Espèces"      (Cash payment)
TRANSFER  = "Virement"     (Bank transfer)
CHECK     = "Chèque"       (Check payment)
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": "Error message",
  "details": {
    "field": ["Error message for this field"]
  }
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request completed successfully |
| 201 | Created | New resource created |
| 400 | Bad Request | Invalid data or missing required fields |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Token is valid but user lacks permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend server error |

### Example Error Responses

**401 Unauthorized (Missing Token):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**400 Bad Request (Validation Error):**
```json
{
  "username": ["This field is required."],
  "password": ["Ensure this field has at least 8 characters."]
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

---

## Rate Limiting

- **General API:** 100 requests per minute per user
- **Authentication:** 10 login attempts per minute per IP
- **File Upload:** 10 MB max file size

If rate limited, you'll receive:

```json
{
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

---

## Examples

### Complete Login Flow

```python
import requests
import json

BASE_URL = "https://api2.bellehouseniger.com/api"

# 1. Login
login_response = requests.post(
    f"{BASE_URL}/auth/login/",
    json={
        "username": "john_doe",
        "password": "secure_password_123"
    }
)

login_data = login_response.json()
access_token = login_data['tokens']['access']
refresh_token = login_data['tokens']['refresh']

# 2. Get user profile
profile_response = requests.get(
    f"{BASE_URL}/app/profile/",
    headers={"Authorization": f"Bearer {access_token}"}
)

profile = profile_response.json()
print(f"Hello {profile['full_name']}!")

# 3. Get projects
projects_response = requests.get(
    f"{BASE_URL}/app/my-projects/",
    headers={"Authorization": f"Bearer {access_token}"}
)

projects = projects_response.json()['results']
for project in projects:
    print(f"- {project['project_name']}: {project['progress_percentage']}% complete")

# 4. Get updates for first project
if projects:
    project_id = projects[0]['id']
    updates_response = requests.get(
        f"{BASE_URL}/app/my-projects/{project_id}/updates/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    updates = updates_response.json()
    print(f"Latest update: {updates[0]['title']}")
```

### Complete Invoice Fetch Flow

```python
import requests

BASE_URL = "https://api2.bellehouseniger.com/api"

# Assuming you have access_token from login
access_token = "your_access_token_here"
headers = {"Authorization": f"Bearer {access_token}"}

# 1. Get all projects
projects_response = requests.get(
    f"{BASE_URL}/app/my-projects/",
    headers=headers
)
projects = projects_response.json()['results']

# 2. Get invoices for first project
project_id = projects[0]['id']
invoices_response = requests.get(
    f"{BASE_URL}/app/my-projects/{project_id}/invoices/",
    headers=headers
)
invoices = invoices_response.json()

# 3. Get detailed information for first invoice
invoice_id = invoices[0]['id']
invoice_detail = requests.get(
    f"{BASE_URL}/app/invoices/{invoice_id}/",
    headers=headers
).json()

# Print invoice details
print(f"Invoice: {invoice_detail['invoice_number']}")
print(f"Status: {invoice_detail['status_display']}")
print(f"Total: {invoice_detail['total_ttc']} CFA")
print("\nLine Items:")
for item in invoice_detail['items']:
    print(f"- {item['description']}: {item['total_price']} CFA")
```

---

## Support & Issues

For API issues or questions:

1. **Check this documentation** - Most issues are covered here
2. **Check Django Admin** - Verify data is correct in admin panel
3. **Review error messages** - They indicate exactly what's wrong
4. **Contact backend team** - If issue persists

**Admin Panel:** `https://api2.bellehouseniger.com/admin/`  
**API Docs (Swagger):** `https://api2.bellehouseniger.com/api/docs/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 2025 | Initial mobile app API release |

