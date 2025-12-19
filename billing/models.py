"""
Billing models for Belle House Backend.

This module contains models for invoicing:
- Invoice: Client invoices with auto-generated numbers
- InvoiceItem: Line items on an invoice
"""

from django.db import models
from django.utils import timezone
from core.models import BaseModel


class Invoice(BaseModel):
    """
    Invoice for a client's active project.
    
    Features:
    - Auto-generated invoice number: BH/{year}/{auto_increment}
    - Client snapshot fields (captured at invoice creation)
    - Computed totals (subtotal, tax, total_ttc, net_to_pay)
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        SENT = 'SENT', 'Envoyé'
        PAID = 'PAID', 'Payé'
        OVERDUE = 'OVERDUE', 'En Retard'
        CANCELLED = 'CANCELLED', 'Annulé'
    
    class PaymentMode(models.TextChoices):
        CASH = 'CASH', 'Espèces'
        TRANSFER = 'TRANSFER', 'Virement'
        CHECK = 'CHECK', 'Chèque'
    
    # Relationship
    project = models.ForeignKey(
        'clients.ActiveProject',
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name="Projet"
    )
    
    # Invoice Number (auto-generated)
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name="Numéro de Facture",
        help_text="Auto-généré: BH/année/numéro"
    )
    
    # Invoice Details
    subject = models.CharField(
        max_length=255,
        verbose_name="Objet",
        help_text="Ex: Plan et suivi"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Statut"
    )
    
    # Dates
    issue_date = models.DateField(
        default=timezone.now,
        verbose_name="Date d'Émission"
    )
    due_date = models.DateField(
        verbose_name="Date d'Échéance"
    )
    
    # Financial
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="TVA (%)"
    )
    advance_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Acompte Versé"
    )
    
    # Payment
    payment_mode = models.CharField(
        max_length=20,
        choices=PaymentMode.choices,
        default=PaymentMode.CASH,
        verbose_name="Mode de Paiement"
    )
    
    # Client Snapshot (captured at invoice creation for historical accuracy)
    client_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nom du Client"
    )
    client_address = models.TextField(
        blank=True,
        verbose_name="Adresse du Client"
    )
    client_phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Téléphone du Client"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Notes additionnelles sur la facture"
    )
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-issue_date', '-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.project.client}"
    
    @property
    def subtotal(self):
        """Sum of all invoice items."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def tax_amount(self):
        """Tax amount based on subtotal and tax percentage."""
        return self.subtotal * (self.tax_percentage / 100)
    
    @property
    def total_ttc(self):
        """Total including tax (TTC = Toutes Taxes Comprises)."""
        return self.subtotal + self.tax_amount
    
    @property
    def net_to_pay(self):
        """Amount remaining after advance payment."""
        return self.total_ttc - self.advance_payment
    
    def generate_invoice_number(self):
        """
        Generate unique invoice number in format: BH/{year}/{auto_increment}
        Example: BH/2025/1, BH/2025/2, etc.
        Counter resets each year.
        """
        current_year = timezone.now().year
        prefix = f"BH/{current_year}/"
        
        # Find the last invoice number for this year
        last_invoice = Invoice.all_objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            try:
                last_num = int(last_invoice.invoice_number.split('/')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num}"
    
    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not set
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Auto-fill client snapshot if empty
        if not self.client_name and self.project_id:
            client = self.project.client
            self.client_name = client.full_name
            self.client_address = client.address
            self.client_phone = client.phone
        
        super().save(*args, **kwargs)


class InvoiceItem(BaseModel):
    """
    Line item on an invoice.
    
    Supports long descriptions for detailed work items.
    """
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Facture"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée du travail"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        verbose_name="Quantité"
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Prix Unitaire"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre"
    )
    
    class Meta:
        verbose_name = "Ligne de Facture"
        verbose_name_plural = "Lignes de Facture"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.description[:50]}... - {self.invoice.invoice_number}"
    
    @property
    def total_price(self):
        """Total price for this line item (quantity * unit_price)."""
        return self.quantity * self.unit_price
