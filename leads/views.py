"""
Views for Leads API.

Public POST endpoints for lead generation.
"""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import ConstructionLead, ContactInquiry
from .serializers import (
    ConstructionLeadCreateSerializer,
    ContactInquiryCreateSerializer
)


class ConstructionLeadCreateView(generics.CreateAPIView):
    """
    Public API endpoint for "Build For Me" form submission.
    
    POST /api/build-for-me/
    """
    permission_classes = [AllowAny]
    serializer_class = ConstructionLeadCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Votre demande a été envoyée avec succès. Nous vous contacterons bientôt.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class ContactInquiryCreateView(generics.CreateAPIView):
    """
    Public API endpoint for contact form submission.
    
    POST /api/contact/
    """
    permission_classes = [AllowAny]
    serializer_class = ContactInquiryCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
