"""
Admin configuration for Billing models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    """Inline for invoice items on Invoice page."""
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'order']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for Invoices with computed totals display."""
    
    list_display = [
        'invoice_number', 'client_name', 'subject', 'status',
        'issue_date', 'due_date', 'display_total_ttc', 'display_net_to_pay', 'is_deleted'
    ]
    list_filter = ['status', 'is_deleted', 'issue_date', 'payment_mode']
    search_fields = ['invoice_number', 'client_name', 'subject']
    date_hierarchy = 'issue_date'
    autocomplete_fields = ['project']
    list_editable = ['status']
    readonly_fields = [
        'invoice_number', 'display_subtotal', 'display_tax_amount',
        'display_total_ttc', 'display_net_to_pay'
    ]
    
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Projet', {
            'fields': ('project',)
        }),
        ('Facture', {
            'fields': ('invoice_number', 'subject', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Client (Auto-rempli)', {
            'fields': ('client_name', 'client_address', 'client_phone'),
            'classes': ('collapse',),
            'description': 'Ces champs sont automatiquement remplis à partir du profil client.'
        }),
        ('Finances', {
            'fields': ('tax_percentage', 'advance_payment', 'payment_mode')
        }),
        ('Totaux Calculés', {
            'fields': ('display_subtotal', 'display_tax_amount', 'display_total_ttc', 'display_net_to_pay'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def get_queryset(self, request):
        return Invoice.all_objects.all()
    
    @admin.display(description="Sous-total")
    def display_subtotal(self, obj):
        value = float(obj.subtotal or 0)
        formatted = "{:,.0f}".format(value)
        return format_html('<strong>{} FCFA</strong>', formatted)
    
    @admin.display(description="TVA")
    def display_tax_amount(self, obj):
        value = float(obj.tax_amount or 0)
        formatted = "{:,.0f}".format(value)
        return format_html('{} FCFA', formatted)
    
    @admin.display(description="Total TTC")
    def display_total_ttc(self, obj):
        value = float(obj.total_ttc or 0)
        formatted = "{:,.0f}".format(value)
        return format_html('<strong>{} FCFA</strong>', formatted)
    
    @admin.display(description="Net à Payer")
    def display_net_to_pay(self, obj):
        value = float(obj.net_to_pay or 0)
        formatted = "{:,.0f}".format(value)
        return format_html('<strong style="color: green;">{} FCFA</strong>', formatted)
    
    actions = ['mark_as_sent', 'mark_as_paid', 'mark_as_overdue']
    
    @admin.action(description="Marquer comme envoyé")
    def mark_as_sent(self, request, queryset):
        queryset.update(status=Invoice.Status.SENT)
    
    @admin.action(description="Marquer comme payé")
    def mark_as_paid(self, request, queryset):
        queryset.update(status=Invoice.Status.PAID)
    
    @admin.action(description="Marquer comme en retard")
    def mark_as_overdue(self, request, queryset):
        queryset.update(status=Invoice.Status.OVERDUE)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """Admin for Invoice Items (for standalone management if needed)."""
    
    list_display = ['invoice', 'description_short', 'quantity', 'unit_price', 'display_total']
    list_filter = ['invoice__status']
    search_fields = ['description', 'invoice__invoice_number']
    raw_id_fields = ['invoice']
    
    def get_queryset(self, request):
        return InvoiceItem.all_objects.all()
    
    @admin.display(description="Description")
    def description_short(self, obj):
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description
    
    @admin.display(description="Total")
    def display_total(self, obj):
        return format_html('{:,.0f} FCFA', obj.total_price)
