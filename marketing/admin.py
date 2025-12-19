"""
Admin configuration for Marketing models.
"""

from django.contrib import admin
from .models import (
    PortfolioItem, PortfolioGalleryImage, PortfolioVideo,
    Service, Partner, Testimonial, BlogPost
)


class PortfolioGalleryImageInline(admin.TabularInline):
    """Inline for gallery images on portfolio item page."""
    model = PortfolioGalleryImage
    extra = 1
    fields = ['image', 'caption', 'order']


class PortfolioVideoInline(admin.TabularInline):
    """Inline for videos on portfolio item page."""
    model = PortfolioVideo
    extra = 1
    fields = ['title', 'video_url', 'order']


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    """Admin for Portfolio items with inline gallery and videos."""
    
    list_display = ['title', 'category', 'city', 'year', 'is_featured', 'order', 'is_deleted']
    list_filter = ['category', 'is_featured', 'is_deleted', 'year', 'city']
    search_fields = ['title', 'description', 'owner', 'city']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_featured']
    
    inlines = [PortfolioGalleryImageInline, PortfolioVideoInline]
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('title', 'slug', 'category', 'main_image', 'description')
        }),
        ('Spécifications du Projet', {
            'fields': ('area', 'task', 'owner', 'contractor', 'year', 'usage')
        }),
        ('Localisation', {
            'fields': ('district', 'city', 'country')
        }),
        ('Affichage', {
            'fields': ('order', 'is_featured')
        }),
    )
    
    def get_queryset(self, request):
        # Show all objects including soft-deleted in admin
        return PortfolioItem.all_objects.all()


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin for Services."""
    
    list_display = ['title', 'order', 'is_active', 'is_deleted']
    list_filter = ['is_active', 'is_deleted']
    search_fields = ['title', 'short_description']
    list_editable = ['order', 'is_active']
    
    def get_queryset(self, request):
        return Service.all_objects.all()


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin for Partners."""
    
    list_display = ['name', 'website', 'order', 'is_active', 'is_deleted']
    list_filter = ['is_active', 'is_deleted']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    
    def get_queryset(self, request):
        return Partner.all_objects.all()


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for Testimonials."""
    
    list_display = ['client_name', 'role', 'rating', 'is_featured', 'is_active', 'is_deleted']
    list_filter = ['rating', 'is_featured', 'is_active', 'is_deleted']
    search_fields = ['client_name', 'content']
    list_editable = ['is_featured', 'is_active']
    
    def get_queryset(self, request):
        return Testimonial.all_objects.all()


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin for Blog Posts."""
    
    list_display = ['title', 'is_published', 'published_date', 'created_at', 'is_deleted']
    list_filter = ['is_published', 'is_deleted', 'published_date']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'thumbnail', 'excerpt', 'content')
        }),
        ('Publication', {
            'fields': ('is_published', 'published_date')
        }),
    )
    
    def get_queryset(self, request):
        return BlogPost.all_objects.all()
