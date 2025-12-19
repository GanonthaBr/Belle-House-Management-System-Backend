"""
URL Configuration for Billing API.

Admin endpoints for invoice management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminInvoiceViewSet

router = DefaultRouter()
router.register(r'invoices', AdminInvoiceViewSet, basename='invoices')

urlpatterns = [
    path('', include(router.urls)),
]
