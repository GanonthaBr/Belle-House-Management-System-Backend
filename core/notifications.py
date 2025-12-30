"""
Notification Services for Belle House Backend.

This module provides:
- Firebase Cloud Messaging (FCM) for push notifications
- Email sending with HTML templates
- Centralized notification dispatcher
"""

import logging
from typing import Optional, List, Dict, Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Firebase initialization (lazy loading)
_firebase_app = None


def get_firebase_app():
    """
    Get or initialize Firebase app.
    Uses lazy loading to avoid initialization errors when credentials are not set.
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    credentials_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
    
    if not credentials_path:
        logger.warning("Firebase credentials not configured. Push notifications disabled.")
        return None
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        cred = credentials.Certificate(credentials_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully.")
        return _firebase_app
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return None


def send_push_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
    image_url: Optional[str] = None
) -> bool:
    """
    Send a push notification to a single device.
    
    Args:
        fcm_token: Device FCM token
        title: Notification title
        body: Notification body text
        data: Optional data payload (key-value pairs, all strings)
        image_url: Optional image URL for rich notifications
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not fcm_token:
        logger.warning("No FCM token provided, skipping push notification.")
        return False
    
    app = get_firebase_app()
    if not app:
        return False
    
    try:
        from firebase_admin import messaging
        
        # Build notification
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url
        )
        
        # Build message
        message = messaging.Message(
            notification=notification,
            data=data or {},
            token=fcm_token,
            # Android specific settings
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#FF5722',
                    sound='default'
                )
            ),
            # iOS specific settings
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1
                    )
                )
            )
        )
        
        # Send message
        response = messaging.send(message)
        logger.info(f"Push notification sent: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False


def send_push_to_multiple(
    fcm_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send push notification to multiple devices.
    
    Args:
        fcm_tokens: List of FCM tokens
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        Dict with success_count and failure_count
    """
    if not fcm_tokens:
        return {'success_count': 0, 'failure_count': 0}
    
    app = get_firebase_app()
    if not app:
        return {'success_count': 0, 'failure_count': len(fcm_tokens)}
    
    try:
        from firebase_admin import messaging
        
        notification = messaging.Notification(title=title, body=body)
        
        message = messaging.MulticastMessage(
            notification=notification,
            data=data or {},
            tokens=fcm_tokens
        )
        
        response = messaging.send_each_for_multicast(message)
        
        logger.info(
            f"Multicast push: {response.success_count} success, "
            f"{response.failure_count} failures"
        )
        
        return {
            'success_count': response.success_count,
            'failure_count': response.failure_count
        }
        
    except Exception as e:
        logger.error(f"Failed to send multicast push: {e}")
        return {'success_count': 0, 'failure_count': len(fcm_tokens)}


def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    from_email: Optional[str] = None
) -> bool:
    """
    Send an HTML email using a template.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        template_name: Template name (without extension, e.g., 'welcome')
        context: Template context variables
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Render HTML template
        html_template = f'emails/{template_name}.html'
        html_content = render_to_string(html_template, context)
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.attach_alternative(html_content, 'text/html')
        
        # Send
        email.send(fail_silently=False)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_simple_email(
    to_email: str,
    subject: str,
    message: str,
    from_email: Optional[str] = None
) -> bool:
    """
    Send a simple text email without template.
    
    Args:
        to_email: Recipient email
        subject: Email subject
        message: Plain text message
        from_email: Sender email
    
    Returns:
        True if sent successfully
    """
    try:
        from django.core.mail import send_mail
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False
        )
        logger.info(f"Simple email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send simple email: {e}")
        return False


# =============================================================================
# HIGH-LEVEL NOTIFICATION FUNCTIONS
# =============================================================================

def notify_project_update(project_update) -> bool:
    """
    Notify client about a project update.
    Sends both push notification and email.
    
    Args:
        project_update: ProjectUpdate model instance
    
    Returns:
        True if at least one notification was sent
    """
    project = project_update.project
    client = project.client
    
    success = False
    
    # Push notification
    if client.fcm_token:
        push_sent = send_push_notification(
            fcm_token=client.fcm_token,
            title=f"Mise à jour: {project.project_name}",
            body=project_update.title,
            data={
                'type': 'project_update',
                'project_id': str(project.id),
                'update_id': str(project_update.id)
            }
        )
        success = success or push_sent
    
    # Email notification
    if client.user.email:
        email_sent = send_email(
            to_email=client.user.email,
            subject=f"Mise à jour de votre projet - {project.project_name}",
            template_name='project_update',
            context={
                'client_name': client.full_name,
                'project_name': project.project_name,
                'update_title': project_update.title,
                'update_description': project_update.description,
                'current_phase': project.get_current_phase_display(),
                'progress': project.progress_percentage
            }
        )
        success = success or email_sent
    
    return success


def notify_new_invoice(invoice) -> bool:
    """
    Notify client about a new invoice.
    
    Args:
        invoice: Invoice model instance
    
    Returns:
        True if notification was sent
    """
    project = invoice.project
    client = project.client
    
    success = False
    
    # Push notification
    if client.fcm_token:
        push_sent = send_push_notification(
            fcm_token=client.fcm_token,
            title="Nouvelle facture",
            body=f"Facture {invoice.invoice_number} - {invoice.net_to_pay:,.0f} FCFA",
            data={
                'type': 'new_invoice',
                'invoice_id': str(invoice.id),
                'project_id': str(project.id)
            }
        )
        success = success or push_sent
    
    # Email notification
    if client.user.email:
        email_sent = send_email(
            to_email=client.user.email,
            subject=f"Facture {invoice.invoice_number} - Belle House",
            template_name='new_invoice',
            context={
                'client_name': client.full_name,
                'invoice_number': invoice.invoice_number,
                'project_name': project.project_name,
                'subject': invoice.subject,
                'subtotal': invoice.subtotal,
                'tax_amount': invoice.tax_amount,
                'total_ttc': invoice.total_ttc,
                'advance_payment': invoice.advance_payment,
                'net_to_pay': invoice.net_to_pay,
                'due_date': invoice.due_date,
                'items': invoice.items.all()
            }
        )
        success = success or email_sent
    
    return success


def notify_welcome(client_profile, temporary_password: Optional[str] = None) -> bool:
    """
    Send welcome notification to new client.
    
    Args:
        client_profile: ClientProfile instance
        temporary_password: Optional temporary password to include
    
    Returns:
        True if sent successfully
    """
    if not client_profile.user.email:
        return False
    
    return send_email(
        to_email=client_profile.user.email,
        subject="Bienvenue chez Belle House!",
        template_name='welcome',
        context={
            'client_name': client_profile.full_name,
            'email': client_profile.user.email,
            'temporary_password': temporary_password,
            'app_url': getattr(settings, 'MOBILE_APP_URL', '#')
        }
    )


def notify_password_reset(user, reset_token: str, reset_url: str) -> bool:
    """
    Send password reset email.
    
    Args:
        user: User instance
        reset_token: Password reset token
        reset_url: Full URL for password reset
    
    Returns:
        True if sent successfully
    """
    return send_email(
        to_email=user.email,
        subject="Réinitialisation de mot de passe - Belle House",
        template_name='password_reset',
        context={
            'user_name': user.get_full_name() or user.username,
            'reset_url': reset_url,
            'reset_token': reset_token
        }
    )
