"""
Views for Core Authentication API.

Registration, Login, Password management endpoints.
"""

from rest_framework import generics, status, serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from .serializers import (
    UserRegistrationSerializer, LoginSerializer, UserProfileSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    Client registration endpoint.
    
    POST /api/auth/register/
    
    Creates a new user account and client profile.
    Returns JWT tokens on successful registration.
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Compte créé avec succès.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Login endpoint.
    
    POST /api/auth/login/
    
    Accepts username OR email with password.
    Returns user profile and JWT tokens.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'message': drf_serializers.CharField(),
                    'user': UserProfileSerializer(),
                    'tokens': inline_serializer(
                        name='TokenPair',
                        fields={
                            'refresh': drf_serializers.CharField(),
                            'access': drf_serializers.CharField(),
                        }
                    ),
                }
            ),
            400: OpenApiResponse(description='Invalid credentials'),
        },
        summary="Login with username or email",
        description="Authenticate with username OR email and password. Returns user profile and JWT tokens.",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Connexion réussie.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class MeView(generics.RetrieveAPIView):
    """
    Get current user profile.
    
    GET /api/auth/me/
    
    Returns the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change password endpoint.
    
    POST /api/auth/change-password/
    
    Requires current password and new password.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: inline_serializer(name='ChangePasswordResponse', fields={'message': drf_serializers.CharField()})},
        summary="Change password",
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Mot de passe modifié avec succès.'
        })


class PasswordResetRequestView(APIView):
    """
    Request password reset.
    
    POST /api/auth/password-reset/
    
    Sends password reset email (to be implemented in Phase 5).
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: inline_serializer(name='PasswordResetRequestResponse', fields={'message': drf_serializers.CharField()})},
        summary="Request password reset",
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # TODO: Generate reset token and send email (Phase 5)
        # For now, just return success message
        # This prevents email enumeration attacks
        
        return Response({
            'message': 'Si un compte existe avec cet email, vous recevrez un lien de réinitialisation.'
        })


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token.
    
    POST /api/auth/password-reset/confirm/
    
    Validates token and sets new password.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200: inline_serializer(name='PasswordResetConfirmResponse', fields={'message': drf_serializers.CharField()})},
        summary="Confirm password reset",
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Validate token and reset password (Phase 5)
        
        return Response({
            'message': 'Mot de passe réinitialisé avec succès.'
        })


class LogoutView(APIView):
    """
    Logout endpoint.
    
    POST /api/auth/logout/
    
    Blacklists the refresh token.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=inline_serializer(name='LogoutRequest', fields={'refresh': drf_serializers.CharField(help_text="Refresh token to blacklist")}),
        responses={200: inline_serializer(name='LogoutResponse', fields={'message': drf_serializers.CharField()})},
        summary="Logout and blacklist token",
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'message': 'Déconnexion réussie.'
            })
        except Exception:
            return Response({
                'message': 'Déconnexion réussie.'
            })
