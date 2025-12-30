"""
URL Configuration for Leads API.

Public endpoints for contact forms.
"""

from django.urls import path
from .views import ConstructionLeadCreateView, ContactInquiryCreateView

urlpatterns = [
    path('build-for-me/', ConstructionLeadCreateView.as_view(), name='build-for-me'),
    path('contact/', ContactInquiryCreateView.as_view(), name='contact'),
]
