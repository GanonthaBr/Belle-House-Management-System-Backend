"""
Django Signals for Clients app.

Handles automatic image compression and business logic.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import compress_image
from .models import ProjectUpdate, AppPromotion


@receiver(post_save, sender=ProjectUpdate)
def compress_project_update_image(sender, instance, created, **kwargs):
    """Compress project update image after save."""
    if instance.image and '_compressed' not in instance.image.name:
        compressed = compress_image(instance.image, max_size=(1200, 900))
        if compressed:
            post_save.disconnect(compress_project_update_image, sender=ProjectUpdate)
            instance.image.save(compressed.name, compressed, save=True)
            post_save.connect(compress_project_update_image, sender=ProjectUpdate)


@receiver(post_save, sender=AppPromotion)
def compress_app_promotion_banner(sender, instance, created, **kwargs):
    """Compress app promotion banner image after save."""
    if instance.banner_image and '_compressed' not in instance.banner_image.name:
        compressed = compress_image(instance.banner_image, max_size=(1200, 600))
        if compressed:
            post_save.disconnect(compress_app_promotion_banner, sender=AppPromotion)
            instance.banner_image.save(compressed.name, compressed, save=True)
            post_save.connect(compress_app_promotion_banner, sender=AppPromotion)
