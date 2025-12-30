"""
URL Configuration for Core Authentication API.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    RegisterView, LoginView, MeView, LogoutView,
    ChangePasswordView, PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    # Registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # Login (custom - returns user profile with tokens)
    path('login/', LoginView.as_view(), name='login'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Current user profile
    path('me/', MeView.as_view(), name='me'),
    
    # JWT Token endpoints (standard)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
