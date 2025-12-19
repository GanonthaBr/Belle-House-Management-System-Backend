"""
URL Configuration for Admin API.

Staff-only endpoints for managing all resources.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Admin views from each app
from marketing.admin_views import (
    AdminPortfolioViewSet, AdminServiceViewSet, AdminPartnerViewSet,
    AdminTestimonialViewSet, AdminBlogPostViewSet
)
from leads.admin_views import (
    AdminConstructionLeadViewSet, AdminContactInquiryViewSet
)
from clients.admin_views import (
    AdminClientViewSet, AdminActiveProjectViewSet,
    AdminProjectUpdateViewSet, AdminPromotionViewSet
)
from billing.views import AdminInvoiceViewSet

router = DefaultRouter()

# Marketing endpoints
router.register(r'portfolio', AdminPortfolioViewSet, basename='admin-portfolio')
router.register(r'services', AdminServiceViewSet, basename='admin-services')
router.register(r'partners', AdminPartnerViewSet, basename='admin-partners')
router.register(r'testimonials', AdminTestimonialViewSet, basename='admin-testimonials')
router.register(r'blog', AdminBlogPostViewSet, basename='admin-blog')

# Leads endpoints
router.register(r'leads', AdminConstructionLeadViewSet, basename='admin-leads')
router.register(r'inquiries', AdminContactInquiryViewSet, basename='admin-inquiries')

# Clients endpoints
router.register(r'clients', AdminClientViewSet, basename='admin-clients')
router.register(r'projects', AdminActiveProjectViewSet, basename='admin-projects')
router.register(r'project-updates', AdminProjectUpdateViewSet, basename='admin-project-updates')
router.register(r'promotions', AdminPromotionViewSet, basename='admin-promotions')

# Billing endpoints
router.register(r'invoices', AdminInvoiceViewSet, basename='admin-invoices')

urlpatterns = [
    path('', include(router.urls)),
]
