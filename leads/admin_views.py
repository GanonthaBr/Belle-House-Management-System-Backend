"""
Admin API Views for Leads models.

Staff-only CRUD endpoints for leads and inquiries.
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import ConstructionLead, ContactInquiry
from .serializers import (
    ConstructionLeadListSerializer, ConstructionLeadDetailSerializer, ConstructionLeadUpdateSerializer,
    ContactInquiryListSerializer, ContactInquiryDetailSerializer
)


class AdminConstructionLeadViewSet(viewsets.ModelViewSet):
    """
    Admin lead management.
    
    list: GET /api/admin/leads/
    retrieve: GET /api/admin/leads/{id}/
    update: PUT/PATCH /api/admin/leads/{id}/
    destroy: DELETE /api/admin/leads/{id}/ (soft delete)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'land_status', 'budget_range']
    search_fields = ['full_name', 'email', 'phone', 'city_or_neighborhood', 'project_details']
    ordering_fields = ['created_at', 'status', 'full_name']
    ordering = ['-created_at']
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']  # No POST - leads come from public form
    
    def get_queryset(self):
        return ConstructionLead.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ConstructionLeadUpdateSerializer
        if self.action == 'retrieve':
            return ConstructionLeadDetailSerializer
        return ConstructionLeadListSerializer
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()
    
    @action(detail=True, methods=['post'])
    def contact(self, request, pk=None):
        """
        Mark lead as contacted.
        
        POST /api/admin/leads/{id}/contact/
        """
        lead = self.get_object()
        lead.status = ConstructionLead.StatusChoices.CONTACTED
        lead.updated_by = request.user
        lead.save()
        return Response({'message': 'Lead marqué comme contacté.'})
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """
        Mark lead as converted (became a client).
        
        POST /api/admin/leads/{id}/convert/
        """
        lead = self.get_object()
        lead.status = ConstructionLead.StatusChoices.CONVERTED
        lead.updated_by = request.user
        lead.save()
        return Response({'message': 'Lead marqué comme converti.'})
    
    @action(detail=True, methods=['post'])
    def mark_lost(self, request, pk=None):
        """
        Mark lead as lost.
        
        POST /api/admin/leads/{id}/mark_lost/
        """
        lead = self.get_object()
        lead.status = ConstructionLead.StatusChoices.LOST
        lead.updated_by = request.user
        lead.save()
        return Response({'message': 'Lead marqué comme perdu.'})


class AdminContactInquiryViewSet(viewsets.ModelViewSet):
    """
    Admin contact inquiry management.
    
    list: GET /api/admin/inquiries/
    retrieve: GET /api/admin/inquiries/{id}/
    destroy: DELETE /api/admin/inquiries/{id}/ (soft delete)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_read']
    search_fields = ['full_name', 'email', 'subject', 'message']
    ordering_fields = ['created_at', 'is_read', 'full_name']
    ordering = ['-created_at']
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']  # Only read, mark as read, delete
    
    def get_queryset(self):
        return ContactInquiry.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContactInquiryDetailSerializer
        return ContactInquiryListSerializer
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()
    
    def retrieve(self, request, *args, **kwargs):
        """Auto-mark as read when viewing detail."""
        instance = self.get_object()
        if not instance.is_read:
            instance.is_read = True
            instance.updated_by = request.user
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark inquiry as read.
        
        POST /api/admin/inquiries/{id}/mark_read/
        """
        inquiry = self.get_object()
        inquiry.is_read = True
        inquiry.updated_by = request.user
        inquiry.save()
        return Response({'message': 'Message marqué comme lu.'})
    
    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """
        Mark inquiry as unread.
        
        POST /api/admin/inquiries/{id}/mark_unread/
        """
        inquiry = self.get_object()
        inquiry.is_read = False
        inquiry.updated_by = request.user
        inquiry.save()
        return Response({'message': 'Message marqué comme non lu.'})
