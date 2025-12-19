"""
Tests for Authentication API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_success(self, api_client, user_data):
        """Test successful user registration."""
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == user_data['email']
    
    def test_register_duplicate_email(self, api_client, user_data, regular_user):
        """Test registration with existing email fails."""
        user_data['email'] = regular_user.email
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields."""
        url = reverse('register')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_weak_password(self, api_client, user_data):
        """Test registration with weak password."""
        user_data['password'] = '123'
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    """Tests for user login endpoint."""
    
    def test_login_with_username_success(self, api_client, regular_user):
        """Test successful login with username."""
        url = reverse('login')
        data = {
            'username': regular_user.username,
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
    
    def test_login_with_email_success(self, api_client, regular_user):
        """Test successful login with email."""
        url = reverse('login')
        data = {
            'email': regular_user.email,
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
    
    def test_login_wrong_password(self, api_client, regular_user):
        """Test login with wrong password."""
        url = reverse('login')
        data = {
            'username': regular_user.username,
            'password': 'WrongPassword!'
        }
        response = api_client.post(url, data, format='json')
        
        # ValidationError returns 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user."""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        # ValidationError returns 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogout:
    """Tests for user logout endpoint."""
    
    def test_logout_success(self, auth_client, regular_user):
        """Test successful logout."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(regular_user)
        url = reverse('logout')
        data = {'refresh': str(refresh)}
        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_logout_unauthenticated(self, api_client):
        """Test logout without authentication."""
        url = reverse('logout')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeEndpoint:
    """Tests for /me/ user profile endpoint."""
    
    def test_get_current_user(self, auth_client, regular_user):
        """Test getting current user profile."""
        url = reverse('me')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == regular_user.email
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test accessing /me/ without authentication."""
        url = reverse('me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestChangePassword:
    """Tests for password change endpoint."""
    
    def test_change_password_success(self, auth_client):
        """Test successful password change."""
        url = reverse('change_password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'NewTestPass456!'
        }
        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old(self, auth_client):
        """Test password change with wrong old password."""
        url = reverse('change_password')
        data = {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'NewTestPass456!'
        }
        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_mismatch(self, auth_client):
        """Test password change with mismatched new passwords."""
        url = reverse('change_password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'DifferentPass789!'
        }
        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJWTTokens:
    """Tests for JWT token endpoints."""
    
    def test_token_obtain(self, api_client, regular_user):
        """Test obtaining JWT tokens."""
        url = reverse('token_obtain_pair')
        data = {
            'username': regular_user.username,
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_token_refresh(self, api_client, regular_user):
        """Test refreshing JWT token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(regular_user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_token_verify(self, api_client, regular_user):
        """Test verifying JWT token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(regular_user)
        url = reverse('token_verify')
        data = {'token': str(refresh.access_token)}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
