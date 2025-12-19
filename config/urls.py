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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # ==========================================================================
    # Authentication Endpoints
    # ==========================================================================
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # ==========================================================================
    # API Documentation
    # ==========================================================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ==========================================================================
    # App-specific URLs (to be added in Phase 3)
    # ==========================================================================
    # path('api/', include('marketing.urls')),
    # path('api/', include('leads.urls')),
    # path('api/app/', include('clients.urls')),
    # path('api/', include('billing.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
