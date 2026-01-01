"""
Admin configuration for Billing models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    """Inline for invoice items on Invoice page."""
    model = InvoiceItem
    extra = 1  # Start with 1 empty row
    min_num = 1  # Require at least 1 item
    fields = ['order', 'description', 'quantity', 'unit_price', 'total_price_display']
    readonly_fields = ['total_price_display']
    ordering = ['order']
    verbose_name = "Ligne de Facture"
    verbose_name_plural = "📦 LIGNES DE FACTURE (Articles/Services)"
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Add help text to fields
        formset.form.base_fields['order'].help_text = "Ordre d'affichage (1, 2, 3...)"
        formset.form.base_fields['description'].help_text = "Ex: Construction dalle béton, Peinture façade..."
        formset.form.base_fields['quantity'].help_text = "Ex: 1, 2.5, 100..."
        formset.form.base_fields['unit_price'].help_text = "Prix unitaire en FCFA"
        return formset
    
    @admin.display(description="Total")
    def total_price_display(self, obj):
        if obj.pk:  # Only show for saved items
            value = float(obj.total_price or 0)
            return format_html('<strong>{:,.0f} FCFA</strong>', value)
        return '-'


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
        'display_total_ttc', 'display_net_to_pay', 'display_help'
    ]
    
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('📋 Instructions', {
            'fields': ('display_help',),
            'classes': ('wide',),
        }),
        ('1️⃣ Sélection du Projet', {
            'fields': ('project',),
            'description': '⚠️ ÉTAPE 1: Choisissez le projet du client. Les infos client seront auto-remplies.'
        }),
        ('2️⃣ Informations de la Facture', {
            'fields': ('invoice_number', 'subject', 'status', 'issue_date', 'due_date'),
            'description': '⚠️ ÉTAPE 2: Le numéro de facture est généré automatiquement. Remplissez le reste.'
        }),
        ('3️⃣ Paramètres Financiers', {
            'fields': ('tax_percentage', 'advance_payment', 'payment_mode'),
            'description': '⚠️ ÉTAPE 3: Configurez la TVA (%) et l\'acompte déjà versé.'
        }),
        ('4️⃣ Articles de la Facture (Scroll Down ⬇️)', {
            'fields': (),
            'description': '⚠️ ÉTAPE 4: DESCENDEZ EN BAS DE PAGE pour ajouter les lignes de facture (description, quantité, prix).'
        }),
        ('✅ Totaux Calculés Automatiquement', {
            'fields': ('display_subtotal', 'display_tax_amount', 'display_total_ttc', 'display_net_to_pay'),
            'description': '💰 Ces montants sont calculés automatiquement après avoir sauvegardé les lignes de facture.'
        }),
        ('📝 Informations Client (Auto-rempli)', {
            'fields': ('client_name', 'client_address', 'client_phone'),
            'classes': ('collapse',),
            'description': 'Ces champs sont automatiquement remplis à partir du profil client.'
        }),
        ('📄 Notes Additionnelles', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def display_help(self, obj):
        """Display help instructions at the top of the form."""
        if obj and obj.pk:
            # Editing existing invoice
            help_html = '''
            <div style="background: #e8f5e9; padding: 15px; border-left: 5px solid #4caf50; margin: 10px 0;">
                <h3 style="margin-top: 0; color: #2e7d32;">✅ Modification de facture</h3>
                <p style="margin: 10px 0;"><strong>Les lignes de facture sont en bas de cette page ⬇️</strong></p>
                <p style="margin: 0;">Descendez pour voir la section "<strong>📦 LIGNES DE FACTURE</strong>" et modifier les articles.</p>
            </div>
            '''
        else:
            # Creating new invoice
            help_html = '''
            <div style="background: #fff3e0; padding: 20px; border-left: 5px solid #ff9800; margin: 10px 0;">
                <h3 style="margin-top: 0; color: #e65100;">📖 Comment créer une facture (PREMIÈRE FOIS):</h3>
                <ol style="line-height: 2;">
                    <li><strong>Choisissez le projet</strong> → Les infos client seront remplies automatiquement</li>
                    <li><strong>Remplissez l'objet, les dates, et la TVA</strong></li>
                    <li><strong>⚠️ Cliquez "ENREGISTRER ET CONTINUER LA MODIFICATION"</strong> en bas</li>
                    <li><strong>La page va se recharger</strong> → Vous verrez alors la section "📦 LIGNES DE FACTURE" apparaître en bas</li>
                    <li><strong>Ajoutez vos lignes de facture</strong> (description, quantité, prix)</li>
                    <li><strong>Cliquez "Enregistrer"</strong> → Les totaux seront calculés</li>
                </ol>
                <p style="margin: 0; padding: 10px; background: #ffebee; border-left: 3px solid #f44336;">
                    <strong>⚠️ TRÈS IMPORTANT:</strong> Vous devez d'abord enregistrer la facture une première fois. 
                    Les lignes de facture n'apparaissent qu'après cette première sauvegarde!
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
