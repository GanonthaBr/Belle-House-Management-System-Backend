"""
URL Configuration for Clients API.

Mobile app endpoints for authenticated clients.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientProfileView, MyProjectsViewSet,
    MyInvoiceDetailView, AppPromotionListView
)

router = DefaultRouter()
router.register(r'my-projects', MyProjectsViewSet, basename='my-projects')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', ClientProfileView.as_view(), name='profile'),
    path('invoices/<int:pk>/', MyInvoiceDetailView.as_view(), name='invoice-detail'),
    path('promotions/', AppPromotionListView.as_view(), name='promotions'),
]
