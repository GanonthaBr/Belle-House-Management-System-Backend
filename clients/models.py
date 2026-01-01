"""
Client portal models for Belle House Backend.

This module contains models for the mobile app client portal:
- ClientProfile: Extended user profile for clients
- ActiveProject: Real contracted projects linked to clients
- ProjectUpdate: Progress updates on active projects
- AppPromotion: Marketing banners shown in the mobile app

IMPORTANT: ActiveProject is for REAL CLIENT CONTRACTS, not marketing content.
For marketing portfolio items, see marketing.PortfolioItem.
"""

from django.db import models
from django.conf import settings
from core.models import BaseModel


class ClientProfile(BaseModel):
    """
    Extended profile for client users (mobile app users).
    
    Linked to Django's User model via OneToOne relationship.
    Contains additional client-specific information.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name="Utilisateur"
    )
    phone = models.CharField(
        max_length=50,
        verbose_name="Téléphone"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Adresse",
        help_text="Adresse complète du client"
    )
    whatsapp_enabled = models.BooleanField(
        default=False,
        verbose_name="WhatsApp Activé",
        help_text="Réservé pour usage futur"
    )
    fcm_token = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Token FCM",
        help_text="Token pour les notifications push"
    )
    
    class Meta:
        verbose_name = "Profil Client"
        verbose_name_plural = "Profils Clients"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        return self.user.email


class ActiveProject(BaseModel):
    """
    Active construction project for a client.
    
    This represents a REAL contracted project being built for a client.
    One client can have MULTIPLE active projects.
    
    IMPORTANT: This is NOT the same as marketing.PortfolioItem.
    PortfolioItem is for marketing showcase only.
    """
    
    class Phase(models.TextChoices):
        CONCEPTION = 'CONCEPTION', 'Conception et Démarches'
        IMPLANTATION = 'IMPLANTATION', 'Implantation'
        FONDATIONS = 'FONDATIONS', 'Fondations'
        ELEVATION_MURS = 'ELEVATION_MURS', 'Élévation des Murs'
        DALLE = 'DALLE', 'Dalle et Acrotère'
        CREPISSAGE = 'CREPISSAGE', 'Crépissage'
        ELECTRICITE_PLOMBERIE = 'ELECTRICITE_PLOMBERIE', 'Électricité & Plomberie'
        RESEAUX = 'RESEAUX', 'Réseaux et Sécurité'
        CARRELAGE_PLAFOND = 'CARRELAGE_PLAFOND', 'Carrelage & Plafonnage'
        PEINTURE_MENUISERIE = 'PEINTURE_MENUISERIE', 'Peinture & Menuiserie'
        EXTERIEUR = 'EXTERIEUR', 'Aménagements Extérieurs'
    
    # Phase to progress percentage mapping (cumulative)
    PHASE_PROGRESS = {
        'CONCEPTION': 5,              # Design & permits
        'IMPLANTATION': 8,            # Site layout
        'FONDATIONS': 23,             # Foundations
        'ELEVATION_MURS': 41,         # Backfill + Form slab + Wall elevation
        'DALLE': 57,                  # Slab prep + Pour + Acrotere
        'CREPISSAGE': 65,             # Exterior + Interior render
        'ELECTRICITE_PLOMBERIE': 81,  # Electrical + Plumbing + Insulation
        'RESEAUX': 87,                # Video + Networks + Fire safety
        'CARRELAGE_PLAFOND': 94,      # Tiling + Ceiling
        'PEINTURE_MENUISERIE': 99,    # Glazing + Painting + Carpentry
        'EXTERIEUR': 100,             # Landscaping + Pool (when applicable)
    }
    
    # Client relationship
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="Client"
    )
    
    # Project Information
    project_name = models.CharField(
        max_length=255,
        verbose_name="Nom du Projet"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Timeline
    start_date = models.DateField(
        verbose_name="Date de Début"
    )
    estimated_completion = models.DateField(
        verbose_name="Date de Fin Estimée"
    )
    
    # Progress
    progress_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name="Progression (%)",
        help_text="Pourcentage de 0 à 100"
    )
    current_phase = models.CharField(
        max_length=30,
        choices=Phase.choices,
        default=Phase.CONCEPTION,
        verbose_name="Phase Actuelle"
    )
    
    # Financial
    total_quote = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Devis Total"
    )
    amount_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Montant Payé"
    )
    
    # Location
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Localisation"
    )
    
    class Meta:
        verbose_name = "Projet Client"
        verbose_name_plural = "Projets Clients"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_name} - {self.client}"
    
    @property
    def remaining_amount(self):
        """Amount remaining to be paid."""
        return self.total_quote - self.amount_paid
    
    @property
    def payment_percentage(self):
        """Percentage of total quote that has been paid."""
        if self.total_quote > 0:
            return round((self.amount_paid / self.total_quote) * 100, 2)
        return 0
    
    def save(self, *args, **kwargs):
        """Auto-calculate progress percentage based on current phase."""
        if self.current_phase:
            self.progress_percentage = self.PHASE_PROGRESS.get(self.current_phase, 0)
        super().save(*args, **kwargs)


class ProjectUpdate(BaseModel):
    """
    Progress update for an active project.
    
    Posted by admin staff to keep clients informed about
    their project's progress. Each update triggers a push notification.
    """
    
    project = models.ForeignKey(
        ActiveProject,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name="Projet"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    image = models.ImageField(
        upload_to='projects/updates/',
        blank=True,
        null=True,
        verbose_name="Photo du Chantier",
        help_text="Télécharger une photo du chantier"
    )
    video_url = models.URLField(
        blank=True,
        verbose_name="Lien Vidéo",
        help_text="Lien YouTube, Vimeo ou autre (optionnel)"
    )
    posted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Publié le"
    )
    
    class Meta:
        verbose_name = "Mise à Jour Projet"
        verbose_name_plural = "Mises à Jour Projets"
        ordering = ['-posted_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.project_name}"


class AppPromotion(BaseModel):
    """
    Marketing banners displayed in the mobile app.
    
    Can link to a portfolio item or an external URL.
    """
    
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )
    banner_image = models.ImageField(
        upload_to='promotions/banners/',
        verbose_name="Image de Bannière"
    )
    linked_portfolio = models.ForeignKey(
        'marketing.PortfolioItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotions',
        verbose_name="Portfolio Lié"
    )
    external_link = models.URLField(
        blank=True,
        verbose_name="Lien Externe"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    class Meta:
        verbose_name = "Promotion App"
        verbose_name_plural = "Promotions App"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
