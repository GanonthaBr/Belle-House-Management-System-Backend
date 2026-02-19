"""
Tests for Billing API endpoints (Admin).
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAdminInvoices:
    """Tests for admin invoice endpoints."""
    
    def test_list_invoices_as_admin(self, admin_client, sample_invoice):
        """Test listing invoices as admin."""
        url = reverse('admin-invoices-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_list_invoices_as_regular_user(self, auth_client, sample_invoice):
        """Test that regular users cannot access admin invoices."""
        url = reverse('admin-invoices-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_invoice(self, admin_client, sample_project):
        """Test creating an invoice."""
        from django.utils import timezone
        from datetime import timedelta
        
        url = reverse('admin-invoices-list')
        data = {
            'project': sample_project.id,
            'subject': 'Phase 2 - Elevation',
            'issue_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'tax_percentage': 18
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'invoice_number' in response.data
        assert response.data['invoice_number'].startswith('BH/')
    
    def test_retrieve_invoice(self, admin_client, sample_invoice):
        """Test retrieving a single invoice."""
        url = reverse('admin-invoices-detail', args=[sample_invoice.id])
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['subject'] == sample_invoice.subject
    
    def test_update_invoice_status(self, admin_client, sample_invoice):
        """Test updating invoice status."""
        url = reverse('admin-invoices-detail', args=[sample_invoice.id])
        data = {'status': 'SENT'}
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_filter_invoices_by_status(self, admin_client, sample_invoice):
        """Test filtering invoices by status."""
        url = reverse('admin-invoices-list')
        response = admin_client.get(url, {'status': 'DRAFT'})
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestInvoiceAutoNumbering:
    """Tests for invoice auto-numbering feature."""
    
    def test_invoice_number_generated(self, admin_client, sample_project):
        """Test that invoice number is auto-generated."""
        from django.utils import timezone
        from datetime import timedelta
        
        url = reverse('admin-invoices-list')
        data = {
            'project': sample_project.id,
            'subject': 'Test Invoice',
            'issue_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'tax_percentage': 18
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['invoice_number'] is not None
        
        # Check format BH/YEAR/NUMBER
        parts = response.data['invoice_number'].split('/')
        assert parts[0] == 'BH'
        assert parts[1] == str(timezone.now().year)
    
    def test_invoice_numbers_increment(self, admin_client, sample_project):
        """Test that invoice numbers increment properly."""
        from django.utils import timezone
        from datetime import timedelta
        
        url = reverse('admin-invoices-list')
        base_data = {
            'project': sample_project.id,
            'issue_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'tax_percentage': 18
        }
        
        # Create first invoice
        data1 = {**base_data, 'subject': 'Invoice 1'}
        response1 = admin_client.post(url, data1, format='json')
        
        # Create second invoice
        data2 = {**base_data, 'subject': 'Invoice 2'}
        response2 = admin_client.post(url, data2, format='json')
        
        # Check numbers are different and incrementing
        num1 = int(response1.data['invoice_number'].split('/')[-1])
        num2 = int(response2.data['invoice_number'].split('/')[-1])
        
        assert num2 == num1 + 1


@pytest.mark.django_db
class TestClientSnapshot:
    """Tests for client snapshot on invoice."""
    
    def test_client_info_captured(self, admin_client, sample_project, client_profile):
        """Test that client info is captured on invoice creation."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Update client info
        client_profile.address = '456 Test Ave, Niamey'
        client_profile.save()
        
        url = reverse('admin-invoices-list')
        data = {
            'project': sample_project.id,
            'subject': 'Test Snapshot',
            'issue_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'tax_percentage': 18
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['client_name'] is not None


@pytest.mark.django_db
class TestAdminProjects:
    """Tests for admin project endpoints."""
    
    def test_list_projects(self, admin_client, sample_project):
        """Test listing projects as admin."""
        url = reverse('admin-projects-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_project(self, admin_client, client_profile):
        """Test creating a project."""
        from django.utils import timezone
        from datetime import timedelta
        
        url = reverse('admin-projects-list')
        data = {
            'client': client_profile.id,
            'project_name': 'New Villa Project',
            'description': 'A new construction project',
            'location': 'Niamey',
            'current_phase': 'FONDATIONS',
            'start_date': timezone.now().date().isoformat(),
            'estimated_completion': (timezone.now().date() + timedelta(days=180)).isoformat()
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_advance_project_phase(self, admin_client, sample_project):
        """Test advancing project phase."""
        url = reverse('admin-projects-advance-phase', args=[sample_project.id])
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh and check phase advanced
        sample_project.refresh_from_db()
        assert sample_project.current_phase == 'ELEVATION_MURS'
