"""
Tests for Clients API endpoints (Mobile App).
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestClientProfile:
    """Tests for client profile endpoints."""
    
    def test_get_profile(self, auth_client, client_profile):
        """Test getting client profile."""
        url = reverse('profile')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == client_profile.phone
    
    def test_update_profile(self, auth_client, client_profile):
        """Test updating client profile."""
        url = reverse('profile')
        data = {
            'phone': '+227 91 11 11 11',
            'address': 'New Address, Niamey'
        }
        response = auth_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == '+227 91 11 11 11'
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test accessing profile without auth."""
        url = reverse('profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMyProjects:
    """Tests for client's projects endpoints."""
    
    def test_list_my_projects(self, auth_client, sample_project):
        """Test listing client's projects."""
        url = reverse('my-projects-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_retrieve_my_project(self, auth_client, sample_project):
        """Test retrieving a single project."""
        url = reverse('my-projects-detail', args=[sample_project.id])
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['project_name'] == sample_project.project_name
    
    def test_project_updates(self, auth_client, sample_project, admin_user):
        """Test getting project updates."""
        from clients.models import ProjectUpdate
        
        ProjectUpdate.objects.create(
            project=sample_project,
            title='Foundation Complete',
            description='Foundation work is done.',
            created_by=admin_user
        )
        
        url = reverse('my-projects-updates', args=[sample_project.id])
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_project_invoices(self, auth_client, sample_invoice):
        """Test getting project invoices."""
        url = reverse('my-projects-invoices', args=[sample_invoice.project.id])
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_cannot_access_other_client_project(self, auth_client, create_user, admin_user, db):
        """Test that client cannot access another client's project."""
        from clients.models import ClientProfile, ActiveProject
        from django.utils import timezone
        from datetime import timedelta
        
        # Create another user with their own project
        other_user = create_user(
            email='other@example.com',
            username='otheruser'
        )
        other_profile = ClientProfile.objects.create(
            user=other_user,
            phone='+227 92 22 22 22'
        )
        other_project = ActiveProject.objects.create(
            client=other_profile,
            project_name='Other Client Project',
            current_phase='FONDATION',
            start_date=timezone.now().date(),
            estimated_completion=timezone.now().date() + timedelta(days=180),
            created_by=admin_user
        )
        
        url = reverse('my-projects-detail', args=[other_project.id])
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFCMToken:
    """Tests for FCM token update endpoint."""
    
    def test_update_fcm_token(self, auth_client, client_profile):
        """Test updating FCM token."""
        url = reverse('fcm-token')
        data = {'fcm_token': 'test-fcm-token-123456'}
        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify token was saved
        client_profile.refresh_from_db()
        assert client_profile.fcm_token == 'test-fcm-token-123456'
    
    def test_update_fcm_token_missing(self, auth_client, client_profile):
        """Test FCM token update with missing token."""
        url = reverse('fcm-token')
        response = auth_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAppPromotions:
    """Tests for app promotions endpoint."""
    
    def test_list_promotions(self, auth_client, admin_user, db):
        """Test listing active promotions."""
        from clients.models import AppPromotion
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a test banner image
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        test_banner = SimpleUploadedFile('banner.png', image_content, content_type='image/png')
        
        AppPromotion.objects.create(
            title='Special Offer',
            banner_image=test_banner,
            is_active=True,
            order=1,
            created_by=admin_user
        )
        
        url = reverse('promotions')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
