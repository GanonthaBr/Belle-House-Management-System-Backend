"""
Admin API Views for Marketing models.

Staff-only CRUD endpoints for portfolio, services, etc.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (
    PortfolioItem, PortfolioGalleryImage, PortfolioVideo,
    Service, Partner, Testimonial, BlogPost
)
from .serializers import (
    PortfolioItemListSerializer, PortfolioItemDetailSerializer, PortfolioItemWriteSerializer,
    ServiceSerializer, PartnerSerializer, TestimonialSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer, BlogPostWriteSerializer
)


class BaseAdminViewSet(viewsets.ModelViewSet):
    """Base ViewSet for admin CRUD operations with soft delete."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class AdminPortfolioViewSet(BaseAdminViewSet):
    """
    Admin portfolio management.
    
    list: GET /api/admin/portfolio/
    retrieve: GET /api/admin/portfolio/{slug}/
    create: POST /api/admin/portfolio/
    update: PUT/PATCH /api/admin/portfolio/{slug}/
    destroy: DELETE /api/admin/portfolio/{slug}/ (soft delete)
    """
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title', 'description', 'city']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return PortfolioItem.objects.prefetch_related('gallery_images', 'videos').all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PortfolioItemWriteSerializer
        if self.action == 'retrieve':
            return PortfolioItemDetailSerializer
        return PortfolioItemListSerializer


class AdminServiceViewSet(BaseAdminViewSet):
    """
    Admin service management.
    
    CRUD for services at /api/admin/services/
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'short_description']
    ordering_fields = ['order', 'title', 'created_at']
    ordering = ['order']


class AdminPartnerViewSet(BaseAdminViewSet):
    """
    Admin partner management.
    
    CRUD for partners at /api/admin/partners/
    """
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order']


class AdminTestimonialViewSet(BaseAdminViewSet):
    """
    Admin testimonial management.
    
    CRUD for testimonials at /api/admin/testimonials/
    """
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured']
    search_fields = ['client_name', 'content', 'role']
    ordering_fields = ['created_at', 'client_name']
    ordering = ['-created_at']


class AdminBlogPostViewSet(BaseAdminViewSet):
    """
    Admin blog management.
    
    CRUD for blog posts at /api/admin/blog/
    """
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'published_date', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return BlogPost.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BlogPostWriteSerializer
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
