"""
URL configuration for Belle House Backend.

API Structure:
- /api/auth/          - Authentication endpoints (JWT tokens, password reset)
- /api/portfolio/     - Public portfolio endpoints
- /api/services/      - Public services endpoints
- /api/partners/      - Public partners endpoints
- /api/testimonials/  - Public testimonials endpoints
- /api/blog/          - Public blog endpoints
- /api/build-for-me/  - Lead generation (construction leads)
- /api/contact/       - Contact form submissions
- /api/app/           - Mobile app endpoints (authenticated)
- /api/admin/         - Admin management endpoints (staff only)
- /api/docs/          - API documentation (Swagger/OpenAPI)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # ==========================================================================
    # Authentication Endpoints (Registration, Login, Password Reset)
    # ==========================================================================
    path('api/auth/', include('core.urls')),
    
    # ==========================================================================
    # API Documentation
    # ==========================================================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ==========================================================================
    # Public API Endpoints (No Authentication)
    # ==========================================================================
    path('api/', include('marketing.urls')),
    path('api/', include('leads.urls')),
    
    # ==========================================================================
    # Mobile App API Endpoints (Client Authentication)
    # ==========================================================================
    path('api/app/', include('clients.urls')),
    
    # ==========================================================================
    # Admin API Endpoints (Staff Authentication)
    # ==========================================================================
    path('api/admin-api/', include('config.admin_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
