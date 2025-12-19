"""
Django Signals for Marketing app.

Handles automatic image compression on model save.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import compress_image
from .models import (
    PortfolioItem, PortfolioGalleryImage, 
    Service, Partner, Testimonial, BlogPost
)


def _compress_and_save(instance, image_field_name, max_size=(1200, 1200)):
    """
    Helper to compress an image field and save if modified.
    Prevents infinite loop by checking if compression is needed.
    """
    image_field = getattr(instance, image_field_name)
    
    if not image_field:
        return
    
    # Skip if already compressed (filename contains '_compressed')
    if '_compressed' in image_field.name:
        return
    
    compressed = compress_image(image_field, max_size=max_size)
    if compressed:
        # Use update() to avoid triggering signal again
        instance.__class__.objects.filter(pk=instance.pk).update(
            **{image_field_name: compressed.name}
        )
        # Actually save the file
        getattr(instance, image_field_name).save(compressed.name, compressed, save=False)


@receiver(post_save, sender=PortfolioItem)
def compress_portfolio_main_image(sender, instance, created, **kwargs):
    """Compress portfolio main image after save."""
    if instance.main_image and '_compressed' not in instance.main_image.name:
        compressed = compress_image(instance.main_image, max_size=(1200, 800))
        if compressed:
            # Disconnect signal temporarily to avoid recursion
            post_save.disconnect(compress_portfolio_main_image, sender=PortfolioItem)
            instance.main_image.save(compressed.name, compressed, save=True)
            post_save.connect(compress_portfolio_main_image, sender=PortfolioItem)


@receiver(post_save, sender=PortfolioGalleryImage)
def compress_gallery_image(sender, instance, created, **kwargs):
    """Compress gallery images after save."""
    if instance.image and '_compressed' not in instance.image.name:
        compressed = compress_image(instance.image, max_size=(1600, 1200))
        if compressed:
            post_save.disconnect(compress_gallery_image, sender=PortfolioGalleryImage)
            instance.image.save(compressed.name, compressed, save=True)
            post_save.connect(compress_gallery_image, sender=PortfolioGalleryImage)


@receiver(post_save, sender=Service)
def compress_service_icon(sender, instance, created, **kwargs):
    """Compress service icon after save."""
    if instance.icon and '_compressed' not in instance.icon.name:
        # Icons should be smaller
        compressed = compress_image(instance.icon, max_size=(256, 256))
        if compressed:
            post_save.disconnect(compress_service_icon, sender=Service)
            instance.icon.save(compressed.name, compressed, save=True)
            post_save.connect(compress_service_icon, sender=Service)


@receiver(post_save, sender=Partner)
def compress_partner_logo(sender, instance, created, **kwargs):
    """Compress partner logo after save."""
    if instance.logo and '_compressed' not in instance.logo.name:
        compressed = compress_image(instance.logo, max_size=(400, 200))
        if compressed:
            post_save.disconnect(compress_partner_logo, sender=Partner)
            instance.logo.save(compressed.name, compressed, save=True)
            post_save.connect(compress_partner_logo, sender=Partner)


@receiver(post_save, sender=Testimonial)
def compress_testimonial_photo(sender, instance, created, **kwargs):
    """Compress testimonial client photo after save."""
    if instance.photo and '_compressed' not in instance.photo.name:
        compressed = compress_image(instance.photo, max_size=(300, 300))
        if compressed:
            post_save.disconnect(compress_testimonial_photo, sender=Testimonial)
            instance.photo.save(compressed.name, compressed, save=True)
            post_save.connect(compress_testimonial_photo, sender=Testimonial)


@receiver(post_save, sender=BlogPost)
def compress_blog_thumbnail(sender, instance, created, **kwargs):
    """Compress blog article thumbnail after save."""
    if instance.thumbnail and '_compressed' not in instance.thumbnail.name:
        compressed = compress_image(instance.thumbnail, max_size=(800, 600))
        if compressed:
            post_save.disconnect(compress_blog_thumbnail, sender=BlogPost)
            instance.thumbnail.save(compressed.name, compressed, save=True)
            post_save.connect(compress_blog_thumbnail, sender=BlogPost)
