"""
URL Configuration for Marketing API.

Public endpoints for website and mobile app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PortfolioItemViewSet, ServiceListView, PartnerListView,
    TestimonialListView, BlogPostViewSet
)

router = DefaultRouter()
router.register(r'portfolio', PortfolioItemViewSet, basename='portfolio')
router.register(r'blog', BlogPostViewSet, basename='blog')

urlpatterns = [
    path('', include(router.urls)),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('partners/', PartnerListView.as_view(), name='partner-list'),
    path('testimonials/', TestimonialListView.as_view(), name='testimonial-list'),
]
