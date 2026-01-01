"""
Admin configuration for Billing models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    """Inline for invoice items on Invoice page."""
    model = InvoiceItem
    extra = 5  # Show 5 empty rows by default (you can add more by clicking "Ajouter une autre ligne")
    min_num = 1  # Require at least 1 item
    can_delete = True  # Show delete checkbox automatically
    fields = ['description', 'quantity', 'unit_price', 'total_price_display']
    readonly_fields = ['total_price_display']
    ordering = ['created_at']
    verbose_name = "Article / Service"
    verbose_name_plural = "📦 ARTICLES DE LA FACTURE - Remplissez ci-dessous (Cochez 'Supprimer' pour retirer)"
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Add help text to fields
        formset.form.base_fields['description'].help_text = "Décrivez l'article ou le service (Ex: Construction dalle béton 50m²)"
        formset.form.base_fields['quantity'].help_text = "Quantité (Ex: 1 pour forfait, 50 pour m², 100 pour sacs...)"
        formset.form.base_fields['unit_price'].help_text = "Prix pour 1 unité en FCFA (Ex: 500000 pour un forfait, 10000 pour le m²)"
        return formset
    
    @admin.display(description="Total Ligne")
    def total_price_display(self, obj):
        if obj.pk:  # Only show for saved items
            value = float(obj.total_price or 0)
            return format_html('<strong style="color: #2e7d32;">{:,.0f} FCFA</strong>', value)
        return format_html('<span style="color: #999;">Calculé après sauvegarde</span>')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for Invoices with computed totals display."""
    
    list_display = [
        'invoice_number', 'client_name', 'subject', 'status',
        'issue_date', 'due_date', 'display_total_ttc', 'display_net_to_pay', 'is_deleted'
    ]
    list_filter = ['status', 'tax_type', 'is_deleted', 'issue_date', 'payment_mode']
    search_fields = ['invoice_number', 'client_name', 'subject']
    date_hierarchy = 'issue_date'
    autocomplete_fields = ['project']
    list_editable = ['status']
    readonly_fields = [
        'invoice_number', 'display_subtotal', 'display_tax_amount',
        'display_total_ttc', 'display_net_to_pay', 'display_help'
    ]
    
    inlines = [InvoiceItemInline]
    
    # Use fieldsets to control layout and prevent automatic tabbing
    fieldsets = (
        (None, {
            'fields': ('display_help',),
        }),
        ('Informations de Base', {
            'fields': (
                'project',
                'invoice_number',
                'subject',
                'status',
                'issue_date',
                'due_date',
            ),
        }),
        ('Configuration des Taxes et Paiement', {
            'fields': (
                'tax_type',
                'tax_percentage',
                'advance_payment',
                'payment_mode',
            ),
        }),
        ('💰 Totaux Calculés Automatiquement', {
            'fields': (
                'display_subtotal',
                'display_tax_amount',
                'display_total_ttc',
                'display_net_to_pay',
            ),
            'classes': ('collapse',),
        }),
        ('Informations Client (Auto-rempli)', {
            'fields': (
                'client_name',
                'client_address',
                'client_phone',
            ),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    def display_help(self, obj):
        """Display help instructions at the top of the form."""
        if obj and obj.pk:
            # Editing existing invoice
            help_html = '''
            <div style="background: #e8f5e9; padding: 15px; border-left: 5px solid #4caf50; margin: 10px 0 20px 0;">
                <h3 style="margin-top: 0; color: #2e7d32;">✅ Modification de facture</h3>
                <p style="margin: 10px 0;"><strong>⬇️ Les articles sont EN BAS DE CETTE PAGE - DESCENDEZ ⬇️</strong></p>
                <ul style="margin: 0; line-height: 1.8;">
                    <li>📜 Faites défiler vers le bas pour voir "📦 ARTICLES DE LA FACTURE"</li>
                    <li>✏️ Modifiez les lignes existantes directement</li>
                    <li>➕ Cliquez "Ajouter une autre ligne de facture" pour ajouter</li>
                    <li>❌ Cochez la case "Supprimer" à droite pour retirer une ligne</li>
                    <li>💰 Type de taxe: ISB (-2%), TVA (+5%), ou personnalisé</li>
                </ul>
            </div>
            '''
        else:
            # Creating new invoice
            help_html = '''
            <div style="background: #fff3e0; padding: 15px; border-left: 5px solid #ff9800; margin: 10px 0 20px 0;">
                <h3 style="margin-top: 0; color: #e65100;">🆕 Nouvelle Facture - Étapes:</h3>
                <ol style="line-height: 1.8; margin: 10px 0;">
                    <li>Remplissez tous les champs ci-dessous (projet, dates, TVA...)</li>
                    <li>Cliquez sur <strong>"ENREGISTRER ET CONTINUER LA MODIFICATION"</strong></li>
                    <li>La page se recharge → Les articles de facture apparaissent en bas</li>
                    <li>5 lignes vides sont affichées (cliquez "Ajouter une autre ligne" pour plus)</li>
                    <li>Remplissez les articles et sauvegardez</li>
                </ol>
                <p style="margin: 0; padding: 8px; background: #ffebee; border-left: 3px solid #f44336; font-weight: bold;">
                    ⚠️ Les articles n'apparaissent qu'après la première sauvegarde!
                </p>
            </div>
            '''
        return format_html(help_html)
    
    display_help.short_description = ""
    
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
    
    def save_model(self, request, obj, form, change):
        """Save the model and set created_by/updated_by."""
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    @admin.action(description="Marquer comme envoyé")
    def mark_as_sent(self, request, queryset):
        queryset.update(status=Invoice.Status.SENT)
    
    @admin.action(description="Marquer comme payé")
    def mark_as_paid(self, request, queryset):
        queryset.update(status=Invoice.Status.PAID)
    
    @admin.action(description="Marquer comme en retard")
    def mark_as_overdue(self, request, queryset):
        queryset.update(status=Invoice.Status.OVERDUE)


# Don't register InvoiceItem separately - it should only be managed via Invoice inline
# This prevents the confusing "Ligne des Facture" button that causes errors
# @admin.register(InvoiceItem)
# class InvoiceItemAdmin(admin.ModelAdmin):
#     """Admin for Invoice Items (for standalone management if needed)."""
#     pass
