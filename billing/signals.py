"""
Django Signals for Billing app.

Handles notifications for invoices.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Invoice

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Invoice)
def notify_client_new_invoice(sender, instance, created, **kwargs):
    """Send notification to client when a new invoice is created."""
    if not created:
        return
    
    # Only send notifications if enabled
    if not getattr(settings, 'ENABLE_NOTIFICATIONS', True):
        return
    
    # Only notify for certain statuses
    if instance.status not in [Invoice.Status.DRAFT, Invoice.Status.SENT]:
        return
    
    try:
        from core.notifications import notify_new_invoice
        notify_new_invoice(instance)
        logger.info(f"Notification sent for invoice: {instance.invoice_number}")
    except Exception as e:
        logger.error(f"Failed to send invoice notification: {e}")
