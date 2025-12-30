"""
Marketing models for Belle House Backend.

This module contains models for the public website content:
- PortfolioItem: Marketing designs (maquettes) and completed works
- PortfolioGalleryImage: Gallery images for portfolio items
- PortfolioVideo: Video links for portfolio items
- Service: Services offered by Belle House
- Partner: Partner companies
- Testimonial: Client testimonials
- BlogPost: Blog articles
"""

from django.db import models
from django.utils.text import slugify
from core.models import BaseModel


class PortfolioItem(BaseModel):
    """
    Marketing portfolio items - designs (maquettes) and completed realizations.
    
    IMPORTANT: These are for MARKETING purposes only and are NOT linked to clients.
    For client projects, see clients.ActiveProject.
    
    Categories:
    - PROJECT: Design maquettes (not built yet, for showcasing capabilities)
    - REALIZATION: Completed works (built and finished, for portfolio showcase)
    """
    
    class Category(models.TextChoices):
        PROJECT = 'PROJECT', 'Projet (Maquette)'
        REALIZATION = 'REALIZATION', 'Réalisation'
    
    # Basic Info
    title = models.CharField(
        max_length=255,
        verbose_name="Nom du Projet"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug URL"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.PROJECT,
        verbose_name="Catégorie"
    )
    main_image = models.ImageField(
        upload_to='portfolio/main/',
        verbose_name="Image Principale"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Project Specifications
    area = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Superficie",
        help_text="Ex: 405,30 m²"
    )
    task = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Tâche",
        help_text="Ex: Conception et Réalisation"
    )
    owner = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Maître d'Ouvrage",
        help_text="Ex: M. Christophe"
    )
    contractor = models.CharField(
        max_length=255,
        default="Belle House",
        verbose_name="Entrepreneur"
    )
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Année"
    )
    usage = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Usage",
        help_text="Ex: Habitation"
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Quartier"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville"
    )
    country = models.CharField(
        max_length=100,
        default="Niger",
        verbose_name="Pays"
    )
    
    # Display order
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Mis en avant"
    )
    
    class Meta:
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while PortfolioItem.all_objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class PortfolioGalleryImage(BaseModel):
    """Gallery images for a portfolio item."""
    
    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name="Portfolio"
    )
    image = models.ImageField(
        upload_to='portfolio/gallery/',
        verbose_name="Image"
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Légende"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre"
    )
    
    class Meta:
        verbose_name = "Image de Galerie"
        verbose_name_plural = "Images de Galerie"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image pour {self.portfolio_item.title}"


class PortfolioVideo(BaseModel):
    """Video links for a portfolio item (YouTube/Vimeo)."""
    
    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name="Portfolio"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )
    video_url = models.URLField(
        verbose_name="URL de la Vidéo",
        help_text="Lien YouTube ou Vimeo"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre"
    )
    
    class Meta:
        verbose_name = "Vidéo Portfolio"
        verbose_name_plural = "Vidéos Portfolio"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.title} - {self.portfolio_item.title}"


class Service(BaseModel):
    """Services offered by Belle House."""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )
    icon = models.ImageField(
        upload_to='services/icons/',
        verbose_name="Icône",
        help_text="SVG ou PNG recommandé"
    )
    short_description = models.TextField(
        verbose_name="Description Courte"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Partner(BaseModel):
    """Partner companies displayed on the website."""
    
    name = models.CharField(
        max_length=255,
        verbose_name="Nom"
    )
    logo = models.ImageField(
        upload_to='partners/logos/',
        verbose_name="Logo"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Site Web"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Testimonial(BaseModel):
    """Client testimonials for the website."""
    
    client_name = models.CharField(
        max_length=255,
        verbose_name="Nom du Client"
    )
    role = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Rôle",
        help_text="Ex: Propriétaire"
    )
    photo = models.ImageField(
        upload_to='testimonials/photos/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    content = models.TextField(
        verbose_name="Témoignage"
    )
    rating = models.PositiveIntegerField(
        default=5,
        verbose_name="Note",
        help_text="Note de 1 à 5"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Mis en avant"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"Témoignage de {self.client_name}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rating < 1 or self.rating > 5:
            raise ValidationError({'rating': 'La note doit être entre 1 et 5.'})


class BlogPost(BaseModel):
    """Blog articles for the website."""
    
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug URL"
    )
    thumbnail = models.ImageField(
        upload_to='blog/thumbnails/',
        verbose_name="Image de Couverture"
    )
    content = models.TextField(
        verbose_name="Contenu"
    )
    excerpt = models.TextField(
        blank=True,
        verbose_name="Extrait",
        help_text="Résumé court pour l'aperçu"
    )
    published_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de Publication"
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Publié"
    )
    
    class Meta:
        verbose_name = "Article de Blog"
        verbose_name_plural = "Articles de Blog"
        ordering = ['-published_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while BlogPost.all_objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
