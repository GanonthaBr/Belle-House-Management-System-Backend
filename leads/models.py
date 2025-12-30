"""
Lead generation models for Belle House Backend.

This module contains models for capturing leads:
- ConstructionLead: "Build For Me" form submissions
- ContactInquiry: General contact form submissions
"""

from django.db import models
from core.models import BaseModel


class ConstructionLead(BaseModel):
    """
    Construction lead from "Build For Me" form.
    
    Captures potential clients interested in having Belle House
    build for them. Can optionally link to a PortfolioItem they
    were interested in (for tracking which designs attract leads).
    """
    
    class Status(models.TextChoices):
        NEW = 'NEW', 'Nouveau'
        CONTACTED = 'CONTACTED', 'Contacté'
        CONVERTED = 'CONVERTED', 'Converti'
        LOST = 'LOST', 'Perdu'
    
    # Contact Information
    name = models.CharField(
        max_length=255,
        verbose_name="Nom Complet"
    )
    phone = models.CharField(
        max_length=50,
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        verbose_name="Email"
    )
    
    # Project Interest
    has_land = models.BooleanField(
        default=False,
        verbose_name="Possède un Terrain"
    )
    location_of_land = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Localisation du Terrain"
    )
    interested_in = models.ForeignKey(
        'marketing.PortfolioItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name="Intéressé par",
        help_text="Quel projet du portfolio a attiré ce lead"
    )
    message = models.TextField(
        blank=True,
        verbose_name="Message",
        help_text="Détails supplémentaires du client"
    )
    
    # Lead Management
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Statut"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes Internes",
        help_text="Notes de suivi par l'équipe"
    )
    
    class Meta:
        verbose_name = "Lead Construction"
        verbose_name_plural = "Leads Construction"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class ContactInquiry(BaseModel):
    """
    General contact form submission.
    
    For simple inquiries from the contact page.
    """
    
    name = models.CharField(
        max_length=255,
        verbose_name="Nom"
    )
    email = models.EmailField(
        verbose_name="Email"
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Téléphone"
    )
    subject = models.CharField(
        max_length=255,
        verbose_name="Sujet"
    )
    message = models.TextField(
        verbose_name="Message"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Lu"
    )
    
    class Meta:
        verbose_name = "Demande de Contact"
        verbose_name_plural = "Demandes de Contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.name}"
