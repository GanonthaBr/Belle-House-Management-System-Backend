"""
Pytest configuration and fixtures for Belle House Backend tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user_data():
    """Return sample user data for registration."""
    return {
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User',
        'phone': '+227 90 00 00 00'
    }


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""
    def _create_user(
        email='user@example.com',
        username='user',
        password='TestPass123!',
        is_staff=False,
        is_superuser=False,
        **kwargs
    ):
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **kwargs
        )
        return user
    return _create_user


@pytest.fixture
def regular_user(create_user):
    """Create a regular user."""
    return create_user(
        email='regular@example.com',
        username='regularuser',
        first_name='Regular',
        last_name='User'
    )


@pytest.fixture
def admin_user(create_user):
    """Create an admin user."""
    return create_user(
        email='admin@example.com',
        username='adminuser',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def auth_client(api_client, regular_user):
    """Return an authenticated API client for regular user."""
    refresh = RefreshToken.for_user(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated API client for admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def client_profile(db, regular_user):
    """Create a client profile for the regular user."""
    from clients.models import ClientProfile
    
    profile, _ = ClientProfile.objects.get_or_create(
        user=regular_user,
        defaults={
            'phone': '+227 90 00 00 00',
            'address': '123 Test Street, Niamey'
        }
    )
    return profile


@pytest.fixture
def sample_project(db, client_profile, admin_user):
    """Create a sample active project."""
    from clients.models import ActiveProject
    from django.utils import timezone
    from datetime import timedelta
    
    project = ActiveProject.objects.create(
        client=client_profile,
        project_name='Test Villa Project',
        description='A test construction project',
        location='Plateau, Niamey',
        current_phase='FONDATION',
        progress_percentage=25,
        total_quote=50000000,
        start_date=timezone.now().date(),
        estimated_completion=timezone.now().date() + timedelta(days=180),
        created_by=admin_user
    )
    return project


@pytest.fixture
def sample_invoice(db, sample_project, admin_user):
    """Create a sample invoice."""
    from billing.models import Invoice
    from django.utils import timezone
    from datetime import timedelta
    
    invoice = Invoice.objects.create(
        project=sample_project,
        subject='Phase 1 - Fondation',
        issue_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=30),
        tax_percentage=18,
        created_by=admin_user
    )
    return invoice


@pytest.fixture
def sample_portfolio_item(db, admin_user):
    """Create a sample portfolio item."""
    from marketing.models import PortfolioItem
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    # Create a simple test image
    image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    test_image = SimpleUploadedFile('test.png', image_content, content_type='image/png')
    
    item = PortfolioItem.objects.create(
        title='Villa Moderne Test',
        slug='villa-moderne-test',
        category='REALIZATION',
        main_image=test_image,
        description='A beautiful modern villa',
        area='350 m²',
        task='Conception et Réalisation',
        owner='M. Test',
        year=2024,
        district='Plateau',
        city='Niamey',
        country='Niger',
        is_featured=True,
        created_by=admin_user
    )
    return item
