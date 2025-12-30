"""
Views for Marketing API.

Public endpoints - no authentication required.
"""

from rest_framework import viewsets, generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    PortfolioItem, PortfolioGalleryImage, PortfolioVideo,
    Service, Partner, Testimonial, BlogPost
)
from .serializers import (
    PortfolioItemListSerializer, PortfolioItemDetailSerializer,
    PortfolioItemWriteSerializer, PortfolioGalleryImageSerializer,
    PortfolioVideoSerializer, ServiceSerializer, PartnerSerializer,
    TestimonialSerializer, BlogPostListSerializer, BlogPostDetailSerializer
)


class PortfolioItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API endpoint for portfolio items.
    
    list: GET /api/portfolio/
    retrieve: GET /api/portfolio/{slug}/
    """
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured', 'city', 'year']
    search_fields = ['title', 'description', 'city', 'district']
    ordering_fields = ['order', 'created_at', 'year']
    ordering = ['order', '-created_at']
    
    def get_queryset(self):
        return PortfolioItem.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PortfolioItemDetailSerializer
        return PortfolioItemListSerializer


class ServiceListView(generics.ListAPIView):
    """
    Public API endpoint for services.
    
    GET /api/services/
    """
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by('order')


class PartnerListView(generics.ListAPIView):
    """
    Public API endpoint for partners.
    
    GET /api/partners/
    """
    permission_classes = [AllowAny]
    serializer_class = PartnerSerializer
    
    def get_queryset(self):
        return Partner.objects.filter(is_active=True).order_by('order')


class TestimonialListView(generics.ListAPIView):
    """
    Public API endpoint for testimonials.
    
    GET /api/testimonials/
    """
    permission_classes = [AllowAny]
    serializer_class = TestimonialSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_featured']
    
    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True)


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API endpoint for blog posts.
    
    list: GET /api/blog/
    retrieve: GET /api/blog/{slug}/
    """
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_date', 'created_at']
    ordering = ['-published_date']
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer
