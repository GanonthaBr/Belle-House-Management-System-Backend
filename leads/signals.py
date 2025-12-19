"""
Django Signals for Leads app.

Handles lead conversion to client and other business logic.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import ConstructionLead

User = get_user_model()


@receiver(pre_save, sender=ConstructionLead)
def track_status_change(sender, instance, **kwargs):
    """Track if status is changing to CONVERTED."""
    if instance.pk:
        try:
            old_instance = ConstructionLead.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except ConstructionLead.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=ConstructionLead)
def convert_lead_to_client(sender, instance, created, **kwargs):
    """
    When a lead status changes to CONVERTED, optionally create a client.
    
    This signal detects when a lead is converted and can automatically
    create a ClientProfile. The admin can also do this manually.
    
    Note: Full automatic conversion is disabled by default to allow
    admin to customize the client creation process. Enable by setting
    AUTO_CONVERT_LEADS = True in settings.
    """
    from django.conf import settings
    from clients.models import ClientProfile
    
    # Check if auto-conversion is enabled
    if not getattr(settings, 'AUTO_CONVERT_LEADS', False):
        return
    
    # Check if status changed to CONVERTED
    old_status = getattr(instance, '_old_status', None)
    if old_status != ConstructionLead.Status.CONVERTED and instance.status == ConstructionLead.Status.CONVERTED:
        # Check if a client with this email already exists
        if User.objects.filter(email=instance.email).exists():
            return
        
        # Create user account
        username = instance.email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=instance.email,
            first_name=instance.name.split()[0] if instance.name else '',
            last_name=' '.join(instance.name.split()[1:]) if len(instance.name.split()) > 1 else '',
            is_active=True
        )
        
        # Set a random password (client will need to reset)
        import secrets
        temp_password = secrets.token_urlsafe(12)
        user.set_password(temp_password)
        user.save()
        
        # Create client profile
        ClientProfile.objects.create(
            user=user,
            phone=instance.phone,
            address=instance.location_of_land or '',
            created_by=instance.updated_by  # The admin who converted
        )
        
        # TODO: Send welcome email with password reset link (Phase 5)
