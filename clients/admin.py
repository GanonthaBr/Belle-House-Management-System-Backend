"""
Admin configuration for Client models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ClientProfile, ActiveProject, ProjectUpdate, AppPromotion


class ClientProfileInline(admin.StackedInline):
    """Inline client profile on User admin page."""
    model = ClientProfile
    can_delete = False
    fk_name = 'user'
    verbose_name_plural = 'Profil Client'


class UserAdmin(BaseUserAdmin):
    """Extended User admin with ClientProfile inline."""
    inlines = [ClientProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ProjectUpdateInline(admin.TabularInline):
    """Inline for project updates on ActiveProject page."""
    model = ProjectUpdate
    extra = 1
    fields = ['title', 'description', 'image', 'posted_at']
    readonly_fields = ['posted_at']


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """Admin for Client Profiles."""
    
    list_display = ['user', 'phone', 'whatsapp_enabled', 'created_at', 'is_deleted']
    list_filter = ['whatsapp_enabled', 'is_deleted']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Contact', {
            'fields': ('phone', 'address', 'whatsapp_enabled')
        }),
        ('Notifications', {
            'fields': ('fcm_token',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return ClientProfile.all_objects.all()


@admin.register(ActiveProject)
class ActiveProjectAdmin(admin.ModelAdmin):
    """Admin for Active Client Projects."""
    
    list_display = [
        'project_name', 'client', 'current_phase', 
        'progress_percentage', 'start_date', 'estimated_completion', 'is_deleted'
    ]
    list_filter = ['current_phase', 'is_deleted', 'start_date']
    search_fields = ['project_name', 'client__user__first_name', 'client__user__last_name', 'location']
    date_hierarchy = 'start_date'
    raw_id_fields = ['client']
    
    inlines = [ProjectUpdateInline]
    
    fieldsets = (
        ('Client', {
            'fields': ('client',)
        }),
        ('Informations du Projet', {
            'fields': ('project_name', 'description', 'location')
        }),
        ('Calendrier', {
            'fields': ('start_date', 'estimated_completion')
        }),
        ('Progression', {
            'fields': ('current_phase', 'progress_percentage')
        }),
        ('Finances', {
            'fields': ('total_quote', 'amount_paid')
        }),
    )
    
    def get_queryset(self, request):
        return ActiveProject.all_objects.all()


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    """Admin for Project Updates."""
    
    list_display = ['title', 'project', 'posted_at', 'is_deleted']
    list_filter = ['is_deleted', 'posted_at']
    search_fields = ['title', 'description', 'project__project_name']
    date_hierarchy = 'posted_at'
    raw_id_fields = ['project']
    
    def get_queryset(self, request):
        return ProjectUpdate.all_objects.all()


@admin.register(AppPromotion)
class AppPromotionAdmin(admin.ModelAdmin):
    """Admin for App Promotions."""
    
    list_display = ['title', 'is_active', 'order', 'linked_portfolio', 'is_deleted']
    list_filter = ['is_active', 'is_deleted']
    search_fields = ['title']
    list_editable = ['is_active', 'order']
    raw_id_fields = ['linked_portfolio']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'banner_image')
        }),
        ('Liens', {
            'fields': ('linked_portfolio', 'external_link')
        }),
        ('Affichage', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def get_queryset(self, request):
        return AppPromotion.all_objects.all()
