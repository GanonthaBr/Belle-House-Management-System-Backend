"""
Example: Custom Admin Enhancements for Belle House

This file shows examples of how to further customize your admin interface.
You can apply these patterns to any of your admin.py files.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Example 1: Enhanced List Display with Custom Fields
class EnhancedClientAdmin(admin.ModelAdmin):
    """
    Example of enhanced client admin with custom styling and actions.
    Apply this pattern to clients/admin.py
    """
    
    list_display = (
        'name',
        'email',
        'phone',
        'status_badge',  # Custom method to show colored badge
        'projects_count',  # Custom method to show project count
        'created_at',
        'action_buttons'  # Custom buttons for quick actions
    )
    
    list_filter = ('created_at', 'status')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'created_at'
    
    # Custom admin actions
    actions = ['mark_as_active', 'mark_as_inactive', 'send_welcome_email']
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'active': '#27ae60',
            'inactive': '#e74c3c',
            'pending': '#f39c12',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Statut')
    
    def projects_count(self, obj):
        """Display count of active projects with link"""
        count = obj.activeproject_set.count()
        if count > 0:
            url = reverse('admin:clients_activeproject_changelist') + f'?client__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #e67e22; font-weight: bold;">{} projets</a>',
                url,
                count
            )
        return format_html('<span style="color: #95a5a6;">0 projets</span>')
    projects_count.short_description = _('Projets')
    
    def action_buttons(self, obj):
        """Custom action buttons"""
        return format_html(
            '<a class="button" href="{}">👁️ Voir</a>&nbsp;'
            '<a class="button" href="{}">✏️ Modifier</a>',
            reverse('admin:clients_client_change', args=[obj.pk]),
            reverse('admin:clients_client_change', args=[obj.pk]),
        )
    action_buttons.short_description = _('Actions')
    action_buttons.allow_tags = True
    
    # Custom admin actions
    @admin.action(description=_('Marquer comme actif'))
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, _(f'{updated} clients marqués comme actifs.'))
    
    @admin.action(description=_('Marquer comme inactif'))
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, _(f'{updated} clients marqués comme inactifs.'))
    
    @admin.action(description=_('Envoyer email de bienvenue'))
    def send_welcome_email(self, request, queryset):
        count = 0
        for client in queryset:
            # Your email sending logic here
            count += 1
        self.message_user(request, _(f'Email de bienvenue envoyé à {count} clients.'))
    
    # Customize form layout
    fieldsets = (
        (_('Informations de Base'), {
            'fields': ('name', 'email', 'phone')
        }),
        (_('Statut'), {
            'fields': ('status',),
            'classes': ('collapse',),
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# Example 2: Inline Models with Custom Display
class ProjectUpdateInline(admin.TabularInline):
    """
    Example of inline editing with custom display.
    Apply this pattern to show related models.
    """
    model = None  # Replace with your ProjectUpdate model
    extra = 1
    fields = ('title', 'description', 'progress_percentage', 'created_at')
    readonly_fields = ('created_at',)
    
    def has_delete_permission(self, request, obj=None):
        # Customize permissions
        return request.user.is_superuser


# Example 3: Dashboard Widgets (Add to admin.py)
class DashboardWidget:
    """
    Custom dashboard widget to show statistics.
    Register in admin.py to show on the admin index page.
    """
    
    @staticmethod
    def get_stats():
        from clients.models import Client, ActiveProject
        from leads.models import ConstructionLead
        from billing.models import Invoice
        
        return {
            'total_clients': Client.objects.count(),
            'active_projects': ActiveProject.objects.filter(status='in_progress').count(),
            'pending_leads': ConstructionLead.objects.filter(status='new').count(),
            'unpaid_invoices': Invoice.objects.filter(status='pending').count(),
        }


# Example 4: Custom Admin Site
class BelleHouseAdminSite(admin.AdminSite):
    """
    Custom admin site with additional functionality.
    To use: Replace default admin.site with this in admin.py files.
    """
    site_header = _('Belle House Administration')
    site_title = _('Belle House Admin')
    index_title = _('Tableau de Bord')
    
    def index(self, request, extra_context=None):
        """
        Custom index page with statistics.
        """
        extra_context = extra_context or {}
        extra_context['stats'] = DashboardWidget.get_stats()
        return super().index(request, extra_context)


# Example 5: Custom Filters
class ProjectStatusFilter(admin.SimpleListFilter):
    """
    Custom filter for project status with French labels.
    """
    title = _('Statut du Projet')
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('in_progress', _('En cours')),
            ('completed', _('Terminé')),
            ('on_hold', _('En pause')),
            ('cancelled', _('Annulé')),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class DateRangeFilter(admin.SimpleListFilter):
    """
    Custom filter for date ranges.
    """
    title = _('Période')
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', _('Aujourd\'hui')),
            ('week', _('Cette semaine')),
            ('month', _('Ce mois')),
            ('year', _('Cette année')),
        )
    
    def queryset(self, request, queryset):
        from datetime import datetime, timedelta
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=datetime.today())
        elif self.value() == 'week':
            start = datetime.today() - timedelta(days=7)
            return queryset.filter(created_at__gte=start)
        elif self.value() == 'month':
            start = datetime.today() - timedelta(days=30)
            return queryset.filter(created_at__gte=start)
        elif self.value() == 'year':
            start = datetime.today() - timedelta(days=365)
            return queryset.filter(created_at__gte=start)
        return queryset


# Example 6: How to Apply These Enhancements

"""
To apply these enhancements to your existing admin files:

1. In clients/admin.py:
   
   from django.contrib import admin
   from .models import Client
   
   @admin.register(Client)
   class ClientAdmin(admin.ModelAdmin):
       list_display = ('name', 'email', 'status_badge', 'projects_count')
       
       def status_badge(self, obj):
           # Copy status_badge method from above
           pass
       
       def projects_count(self, obj):
           # Copy projects_count method from above
           pass

2. In leads/admin.py:
   
   from django.contrib import admin
   from .models import ConstructionLead
   
   @admin.register(ConstructionLead)
   class LeadAdmin(admin.ModelAdmin):
       list_display = ('client_name', 'email', 'service', 'status_badge', 'created_at')
       list_filter = ('status', 'service', DateRangeFilter)
       actions = ['mark_as_contacted', 'mark_as_converted']

3. In billing/admin.py:
   
   from django.contrib import admin
   from .models import Invoice
   
   @admin.register(Invoice)
   class InvoiceAdmin(admin.ModelAdmin):
       list_display = ('invoice_number', 'client', 'amount_badge', 'status_badge', 'due_date')
       list_filter = ('status', DateRangeFilter)
       
       def amount_badge(self, obj):
           return format_html(
               '<span style="font-weight: bold; color: #27ae60;">{:,.0f} FCFA</span>',
               obj.total_amount
           )
"""

# Remember to import these in your actual admin.py files!
