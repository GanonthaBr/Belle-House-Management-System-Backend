"""
Admin configuration for Lead models.
"""

from django.contrib import admin
from .models import ConstructionLead, ContactInquiry


@admin.register(ConstructionLead)
class ConstructionLeadAdmin(admin.ModelAdmin):
    """Admin for Construction Leads."""
    
    list_display = ['name', 'phone', 'email', 'status', 'has_land', 'interested_in', 'created_at', 'is_deleted']
    list_filter = ['status', 'has_land', 'is_deleted', 'created_at']
    search_fields = ['name', 'email', 'phone', 'location_of_land', 'message']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de Contact', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Intérêt', {
            'fields': ('has_land', 'location_of_land', 'interested_in', 'message')
        }),
        ('Gestion du Lead', {
            'fields': ('status', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return ConstructionLead.all_objects.all()
    
    actions = ['mark_as_contacted', 'mark_as_converted', 'mark_as_lost']
    
    @admin.action(description="Marquer comme contacté")
    def mark_as_contacted(self, request, queryset):
        queryset.update(status=ConstructionLead.Status.CONTACTED)
    
    @admin.action(description="Marquer comme converti")
    def mark_as_converted(self, request, queryset):
        queryset.update(status=ConstructionLead.Status.CONVERTED)
    
    @admin.action(description="Marquer comme perdu")
    def mark_as_lost(self, request, queryset):
        queryset.update(status=ConstructionLead.Status.LOST)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    """Admin for Contact Inquiries."""
    
    list_display = ['subject', 'name', 'email', 'is_read', 'created_at', 'is_deleted']
    list_filter = ['is_read', 'is_deleted', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Statut', {
            'fields': ('is_read',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return ContactInquiry.all_objects.all()
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    @admin.action(description="Marquer comme lu")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    
    @admin.action(description="Marquer comme non lu")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
