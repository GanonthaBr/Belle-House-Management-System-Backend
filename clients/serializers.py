"""
Serializers for Clients API.

Mobile app endpoints for authenticated clients.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ClientProfile, ActiveProject, ProjectUpdate, AppPromotion
from billing.serializers import InvoiceListSerializer


# =============================================================================
# USER & PROFILE SERIALIZERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class ClientProfileSerializer(serializers.ModelSerializer):
    """Serializer for client profile (mobile app)."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'full_name', 'email',
            'phone', 'address', 'whatsapp_enabled', 'fcm_token'
        ]
        read_only_fields = ['id', 'user', 'full_name', 'email']


class ClientProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating client profile (mobile app)."""
    
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = ClientProfile
        fields = ['phone', 'address', 'fcm_token', 'first_name', 'last_name']
    
    def update(self, instance, validated_data):
        # Update user fields if provided
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        
        if first_name is not None:
            instance.user.first_name = first_name
        if last_name is not None:
            instance.user.last_name = last_name
        if first_name or last_name:
            instance.user.save()
        
        # Update profile fields
        return super().update(instance, validated_data)


# =============================================================================
# PROJECT UPDATE SERIALIZERS
# =============================================================================

class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for project updates."""
    
    class Meta:
        model = ProjectUpdate
        fields = [
            'id', 'title', 'description', 'image', 'posted_at'
        ]


class ProjectUpdateWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating project updates (admin use)."""
    
    class Meta:
        model = ProjectUpdate
        fields = ['project', 'title', 'description', 'image']


# =============================================================================
# ACTIVE PROJECT SERIALIZERS
# =============================================================================

class ActiveProjectListSerializer(serializers.ModelSerializer):
    """Serializer for active project list (lightweight)."""
    
    current_phase_display = serializers.CharField(source='get_current_phase_display', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    payment_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = ActiveProject
        fields = [
            'id', 'project_name', 'start_date', 'estimated_completion',
            'progress_percentage', 'current_phase', 'current_phase_display',
            'total_quote', 'amount_paid', 'remaining_amount', 'payment_percentage',
            'location'
        ]


class ActiveProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for active project detail (full data with updates and invoices)."""
    
    current_phase_display = serializers.CharField(source='get_current_phase_display', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    payment_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    updates = ProjectUpdateSerializer(many=True, read_only=True)
    invoices = InvoiceListSerializer(many=True, read_only=True)
    
    class Meta:
        model = ActiveProject
        fields = [
            'id', 'project_name', 'description', 'location',
            'start_date', 'estimated_completion',
            'progress_percentage', 'current_phase', 'current_phase_display',
            'total_quote', 'amount_paid', 'remaining_amount', 'payment_percentage',
            'updates', 'invoices',
            'created_at', 'updated_at'
        ]


class ActiveProjectWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating active projects (admin use)."""
    
    class Meta:
        model = ActiveProject
        fields = [
            'client', 'project_name', 'description', 'location',
            'start_date', 'estimated_completion',
            'progress_percentage', 'current_phase',
            'total_quote', 'amount_paid'
        ]


# =============================================================================
# APP PROMOTION SERIALIZERS
# =============================================================================

class AppPromotionSerializer(serializers.ModelSerializer):
    """Serializer for app promotions (mobile app banners)."""
    
    linked_portfolio_slug = serializers.CharField(
        source='linked_portfolio.slug',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = AppPromotion
        fields = [
            'id', 'title', 'banner_image',
            'linked_portfolio', 'linked_portfolio_slug',
            'external_link', 'order'
        ]


class AppPromotionWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating app promotions (admin use)."""
    
    class Meta:
        model = AppPromotion
        fields = [
            'title', 'banner_image',
            'linked_portfolio', 'external_link',
            'order', 'is_active'
        ]


# =============================================================================
# ADMIN CLIENT MANAGEMENT SERIALIZERS
# =============================================================================

class ClientProfileAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin client management."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'full_name', 'email',
            'phone', 'address', 'whatsapp_enabled',
            'projects_count', 'created_at'
        ]
    
    def get_projects_count(self, obj):
        return obj.projects.count()


class ClientCreateSerializer(serializers.Serializer):
    """Serializer for creating a new client (admin use)."""
    
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=50)
    address = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Cet email existe déjà.")
        return value.lower()
    
    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        
        # Generate password if not provided
        password = validated_data.pop('password', None)
        if not password:
            password = get_random_string(12)
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password
        )
        
        # Create client profile
        client_profile = ClientProfile.objects.create(
            user=user,
            phone=validated_data['phone'],
            address=validated_data.get('address', '')
        )
        
        # Store password for notification (will be sent via email)
        client_profile._generated_password = password
        
        return client_profile
