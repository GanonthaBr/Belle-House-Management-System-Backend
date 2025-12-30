"""
Serializers for Marketing API.

Public endpoints - no authentication required.
"""

from rest_framework import serializers
from .models import (
    PortfolioItem, PortfolioGalleryImage, PortfolioVideo,
    Service, Partner, Testimonial, BlogPost
)


class PortfolioGalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for portfolio gallery images."""
    
    class Meta:
        model = PortfolioGalleryImage
        fields = ['id', 'image', 'caption', 'order']


class PortfolioVideoSerializer(serializers.ModelSerializer):
    """Serializer for portfolio videos."""
    
    class Meta:
        model = PortfolioVideo
        fields = ['id', 'title', 'video_url', 'order']


class PortfolioItemListSerializer(serializers.ModelSerializer):
    """Serializer for portfolio list view (lightweight)."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'title', 'slug', 'category', 'category_display',
            'main_image', 'area', 'city', 'year', 'is_featured', 'order'
        ]


class PortfolioItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for portfolio detail view (full data with nested gallery/videos)."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    gallery_images = PortfolioGalleryImageSerializer(many=True, read_only=True)
    videos = PortfolioVideoSerializer(many=True, read_only=True)
    
    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'title', 'slug', 'category', 'category_display',
            'main_image', 'description',
            # Specifications
            'area', 'task', 'owner', 'contractor', 'year', 'usage',
            # Location
            'district', 'city', 'country',
            # Display
            'order', 'is_featured',
            # Nested
            'gallery_images', 'videos',
            # Timestamps
            'created_at', 'updated_at'
        ]


class PortfolioItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating portfolio items (admin use)."""
    
    class Meta:
        model = PortfolioItem
        fields = [
            'title', 'slug', 'category', 'main_image', 'description',
            'area', 'task', 'owner', 'contractor', 'year', 'usage',
            'district', 'city', 'country', 'order', 'is_featured'
        ]
        extra_kwargs = {
            'slug': {'required': False}
        }


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for services."""
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'icon', 'short_description', 'order']


class PartnerSerializer(serializers.ModelSerializer):
    """Serializer for partners."""
    
    class Meta:
        model = Partner
        fields = ['id', 'name', 'logo', 'website', 'order']


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials."""
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'role', 'photo', 'content',
            'rating', 'is_featured'
        ]


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post list view."""
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'thumbnail', 'excerpt',
            'published_date', 'created_at'
        ]


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for blog post detail view."""
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'thumbnail', 'content', 'excerpt',
            'published_date', 'is_published', 'created_at', 'updated_at'
        ]


class BlogPostWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating blog posts (admin use)."""
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'thumbnail', 'content', 'excerpt',
            'published_date', 'is_published'
        ]
        extra_kwargs = {
            'slug': {'required': False}
        }
