"""
Serializers for Leads API.

Public POST endpoints for lead generation.
"""

from rest_framework import serializers
from .models import ConstructionLead, ContactInquiry


class ConstructionLeadCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating construction leads (public "Build For Me" form).
    
    Only accepts fields that a visitor would fill out.
    Status and notes are managed internally.
    """
    
    class Meta:
        model = ConstructionLead
        fields = [
            'name', 'phone', 'email',
            'has_land', 'location_of_land',
            'interested_in', 'message'
        ]
    
    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()


class ConstructionLeadListSerializer(serializers.ModelSerializer):
    """Serializer for listing construction leads (admin use)."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interested_in_title = serializers.CharField(
        source='interested_in.title', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = ConstructionLead
        fields = [
            'id', 'name', 'phone', 'email',
            'has_land', 'location_of_land',
            'interested_in', 'interested_in_title', 'message',
            'status', 'status_display', 'notes',
            'created_at', 'updated_at'
        ]


class ConstructionLeadDetailSerializer(serializers.ModelSerializer):
    """Serializer for construction lead detail view (admin use)."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interested_in_title = serializers.CharField(
        source='interested_in.title', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = ConstructionLead
        fields = [
            'id', 'name', 'phone', 'email',
            'has_land', 'location_of_land',
            'interested_in', 'interested_in_title', 'message',
            'status', 'status_display', 'notes',
            'created_at', 'updated_at'
        ]


class ConstructionLeadUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating construction leads (admin use)."""
    
    class Meta:
        model = ConstructionLead
        fields = ['status', 'notes']


class ContactInquiryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact inquiries (public contact form).
    """
    
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'subject', 'message']
    
    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()


class ContactInquiryListSerializer(serializers.ModelSerializer):
    """Serializer for listing contact inquiries (admin use)."""
    
    class Meta:
        model = ContactInquiry
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'is_read', 'created_at', 'updated_at'
        ]


class ContactInquiryDetailSerializer(serializers.ModelSerializer):
    """Serializer for contact inquiry detail view (admin use)."""
    
    class Meta:
        model = ContactInquiry
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'is_read', 'created_at', 'updated_at'
        ]


class ContactInquiryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating contact inquiry (admin use)."""
    
    class Meta:
        model = ContactInquiry
        fields = ['is_read']
