"""
Tests for Marketing API endpoints (Public).
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPortfolioEndpoints:
    """Tests for public portfolio endpoints."""
    
    def test_list_portfolio_items(self, api_client, sample_portfolio_item):
        """Test listing published portfolio items."""
        url = reverse('portfolio-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
    
    def test_retrieve_portfolio_item(self, api_client, sample_portfolio_item):
        """Test retrieving a single portfolio item."""
        # Portfolio uses slug as lookup field
        url = reverse('portfolio-detail', args=[sample_portfolio_item.slug])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == sample_portfolio_item.title
    
    def test_filter_portfolio_by_category(self, api_client, sample_portfolio_item):
        """Test filtering portfolio by category."""
        url = reverse('portfolio-list')
        response = api_client.get(url, {'category': 'REALIZATION'})
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_filter_portfolio_featured(self, api_client, sample_portfolio_item):
        """Test filtering featured portfolio items."""
        url = reverse('portfolio-list')
        response = api_client.get(url, {'is_featured': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_portfolio(self, api_client, sample_portfolio_item):
        """Test searching portfolio items."""
        url = reverse('portfolio-list')
        response = api_client.get(url, {'search': 'Villa'})
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestServiceEndpoints:
    """Tests for public service endpoints."""
    
    def test_list_services(self, api_client, db):
        """Test listing services."""
        from marketing.models import Service
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a simple test image for icon
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        test_icon = SimpleUploadedFile('icon.png', image_content, content_type='image/png')
        
        Service.objects.create(
            title='Construction',
            icon=test_icon,
            short_description='Construction de maisons',
            order=1,
            is_active=True
        )
        
        url = reverse('service-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTestimonialEndpoints:
    """Tests for public testimonial endpoints."""
    
    def test_list_testimonials(self, api_client, db):
        """Test listing testimonials."""
        from marketing.models import Testimonial
        
        Testimonial.objects.create(
            client_name='M. Test',
            content='Excellent service!',
            rating=5,
            is_active=True
        )
        
        url = reverse('testimonial-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestBlogEndpoints:
    """Tests for public blog endpoints."""
    
    def test_list_blog_posts(self, api_client, admin_user, db):
        """Test listing blog posts."""
        from marketing.models import BlogPost
        from django.utils import timezone
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a test thumbnail image
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        test_thumbnail = SimpleUploadedFile('thumb.png', image_content, content_type='image/png')
        
        BlogPost.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content here.',
            thumbnail=test_thumbnail,
            is_published=True,
            published_date=timezone.now()
        )
        
        url = reverse('blog-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPartnerEndpoints:
    """Tests for public partner endpoints."""
    
    def test_list_partners(self, api_client, db):
        """Test listing partners."""
        from marketing.models import Partner
        
        Partner.objects.create(
            name='Test Partner',
            is_active=True,
            order=1
        )
        
        url = reverse('partner-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestContactInquiry:
    """Tests for contact form submission."""
    
    def test_submit_contact_inquiry(self, api_client):
        """Test submitting a contact inquiry."""
        url = reverse('contact')
        data = {
            'name': 'Test Person',
            'email': 'test@example.com',
            'phone': '+227 90 00 00 00',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_submit_contact_missing_fields(self, api_client):
        """Test contact submission with missing fields."""
        url = reverse('contact')
        data = {'name': 'Test'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestConstructionLead:
    """Tests for construction lead submission."""
    
    def test_submit_construction_lead(self, api_client, sample_portfolio_item):
        """Test submitting a construction lead."""
        url = reverse('build-for-me')
        data = {
            'name': 'Test Client',
            'email': 'client@example.com',
            'phone': '+227 90 00 00 00',
            'has_land': True,
            'location_of_land': 'Niamey',
            'interested_in': sample_portfolio_item.id,
            'message': 'I want to build this house.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
