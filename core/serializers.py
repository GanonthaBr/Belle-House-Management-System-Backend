"""
Serializers for Core Authentication API.

Registration, Login, Password Reset endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from clients.models import ClientProfile


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for client registration (mobile app signup).
    
    Creates both User and ClientProfile.
    """
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=50)
    
    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        phone = validated_data.pop('phone')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Create client profile
        ClientProfile.objects.create(
            user=user,
            phone=phone
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login.
    
    Accepts username OR email with password.
    """
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not username and not email:
            raise serializers.ValidationError(
                "Veuillez fournir un nom d'utilisateur ou un email."
            )
        
        # If email provided, find username
        if email and not username:
            try:
                user = User.objects.get(email=email.lower())
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'email': "Aucun compte trouvé avec cet email."
                })
        
        # Authenticate
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError(
                "Identifiants invalides."
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "Ce compte a été désactivé."
            )
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile in login response."""
    
    phone = serializers.CharField(source='client_profile.phone', read_only=True)
    address = serializers.CharField(source='client_profile.address', read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'address', 'is_staff'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Les mots de passe ne correspondent pas."
            })
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        email = value.lower()
        if not User.objects.filter(email=email).exists():
            # Don't reveal if email exists or not (security)
            pass
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with token."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Les mots de passe ne correspondent pas."
            })
        return attrs
