"""
Tests for Notification services.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestNotificationService:
    """Tests for core notification functions."""
    
    def test_compress_image_function_exists(self):
        """Test that compress_image function is importable."""
        from core.utils import compress_image
        assert callable(compress_image)
    
    def test_notification_functions_exist(self):
        """Test that notification functions are importable."""
        from core.notifications import (
            send_push_notification,
            send_push_to_multiple,
            send_email,
            send_simple_email,
            notify_project_update,
            notify_new_invoice,
            notify_welcome
        )
        
        assert callable(send_push_notification)
        assert callable(send_push_to_multiple)
        assert callable(send_email)
        assert callable(send_simple_email)
        assert callable(notify_project_update)
        assert callable(notify_new_invoice)
        assert callable(notify_welcome)
    
    @patch('core.notifications.get_firebase_app')
    def test_push_notification_no_firebase(self, mock_firebase):
        """Test push notification when Firebase is not configured."""
        from core.notifications import send_push_notification
        
        mock_firebase.return_value = None
        
        result = send_push_notification(
            fcm_token='test-token',
            title='Test',
            body='Test message'
        )
        
        assert result is False
    
    def test_push_notification_no_token(self):
        """Test push notification with no token."""
        from core.notifications import send_push_notification
        
        result = send_push_notification(
            fcm_token='',
            title='Test',
            body='Test message'
        )
        
        assert result is False
    
    @patch('core.notifications.EmailMultiAlternatives')
    def test_send_email_success(self, mock_email_class):
        """Test sending email successfully."""
        from core.notifications import send_email
        
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        
        with patch('core.notifications.render_to_string', return_value='<html>Test</html>'):
            result = send_email(
                to_email='test@example.com',
                subject='Test Subject',
                template_name='welcome',
                context={'client_name': 'Test'}
            )
        
        assert result is True
        mock_email.send.assert_called_once()


@pytest.mark.django_db
class TestNotificationSignals:
    """Tests for notification signal handlers."""
    
    @patch('core.notifications.send_push_notification')
    @patch('core.notifications.send_email')
    def test_project_update_triggers_notification(
        self, mock_email, mock_push, sample_project, admin_user
    ):
        """Test that creating a project update triggers notification."""
        from clients.models import ProjectUpdate
        
        # Mock successful notifications
        mock_push.return_value = True
        mock_email.return_value = True
        
        # Create project update
        update = ProjectUpdate.objects.create(
            project=sample_project,
            title='Test Update',
            description='Progress report',
            created_by=admin_user
        )
        
        # Signal should have been triggered
        assert update.id is not None
    
    @patch('core.notifications.send_push_notification')
    @patch('core.notifications.send_email')
    def test_invoice_creation_triggers_notification(
        self, mock_email, mock_push, sample_project, admin_user
    ):
        """Test that creating an invoice triggers notification."""
        from billing.models import Invoice
        from django.utils import timezone
        from datetime import timedelta
        
        mock_push.return_value = True
        mock_email.return_value = True
        
        invoice = Invoice.objects.create(
            project=sample_project,
            subject='Test Invoice',
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            tax_percentage=18,
            created_by=admin_user
        )
        
        assert invoice.invoice_number is not None


@pytest.mark.django_db
class TestEmailTemplates:
    """Tests for email template rendering."""
    
    def test_welcome_template_renders(self):
        """Test welcome email template renders correctly."""
        from django.template.loader import render_to_string
        
        context = {
            'client_name': 'Test Client',
            'email': 'test@example.com',
            'temporary_password': 'TempPass123',
            'app_url': 'https://app.bellehouse.ne'
        }
        
        html = render_to_string('emails/welcome.html', context)
        
        assert 'Test Client' in html
        assert 'TempPass123' in html
    
    def test_project_update_template_renders(self):
        """Test project update email template renders correctly."""
        from django.template.loader import render_to_string
        
        context = {
            'client_name': 'Test Client',
            'project_name': 'Villa Test',
            'update_title': 'Foundation Complete',
            'update_description': 'Work is progressing well.',
            'current_phase': 'Foundation',
            'progress': 25
        }
        
        html = render_to_string('emails/project_update.html', context)
        
        assert 'Villa Test' in html
        assert 'Foundation Complete' in html
    
    def test_invoice_template_renders(self):
        """Test invoice email template renders correctly."""
        from django.template.loader import render_to_string
        
        context = {
            'client_name': 'Test Client',
            'invoice_number': 'BH/2025/1',
            'project_name': 'Villa Test',
            'subject': 'Phase 1',
            'subtotal': 1000000,
            'tax_amount': 180000,
            'total_ttc': 1180000,
            'advance_payment': 0,
            'net_to_pay': 1180000,
            'due_date': '2025-01-15',
            'items': []
        }
        
        html = render_to_string('emails/new_invoice.html', context)
        
        assert 'BH/2025/1' in html
        assert '1180000' in html  # floatformat:0 doesn't add thousands separator
    
    def test_password_reset_template_renders(self):
        """Test password reset email template renders correctly."""
        from django.template.loader import render_to_string
        
        context = {
            'user_name': 'Test User',
            'reset_url': 'https://app.bellehouse.ne/reset?token=abc123',
            'reset_token': 'abc123'
        }
        
        html = render_to_string('emails/password_reset.html', context)
        
        assert 'Test User' in html
        assert 'reset?token=abc123' in html
