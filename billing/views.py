"""
Views for Billing API.

Admin endpoints for invoice management.
Client endpoints are in clients.views (MyInvoiceDetailView).
"""

from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Invoice, InvoiceItem
from .serializers import (
    InvoiceListSerializer, InvoiceDetailSerializer, InvoiceWriteSerializer,
    InvoiceItemSerializer
)


# =============================================================================
# ADMIN API VIEWS (Staff Role)
# =============================================================================

class AdminInvoiceViewSet(viewsets.ModelViewSet):
    """
    Admin invoice management endpoint.
    
    list: GET /api/admin/invoices/
    retrieve: GET /api/admin/invoices/{id}/
    create: POST /api/admin/invoices/
    update: PUT/PATCH /api/admin/invoices/{id}/
    destroy: DELETE /api/admin/invoices/{id}/ (soft delete)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'project__client']
    search_fields = ['invoice_number', 'project__name', 'project__client__user__first_name', 'project__client__user__last_name']
    ordering_fields = ['issue_date', 'due_date', 'total_ttc', 'created_at']
    ordering = ['-issue_date']
    
    def get_queryset(self):
        return Invoice.objects.select_related('project', 'project__client', 'project__client__user').prefetch_related('items').all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InvoiceWriteSerializer
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceListSerializer
    
    def create(self, request, *args, **kwargs):
        """Override to return detailed response with invoice_number."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Return with detail serializer to include invoice_number
        output_serializer = InvoiceDetailSerializer(serializer.instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete"""
        from django.utils import timezone
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark invoice as paid.
        
        POST /api/admin/invoices/{id}/mark_paid/
        """
        invoice = self.get_object()
        invoice.status = Invoice.StatusChoices.PAID
        invoice.updated_by = request.user
        invoice.save()
        return Response({'message': 'Facture marquée comme payée.'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel invoice.
        
        POST /api/admin/invoices/{id}/cancel/
        """
        invoice = self.get_object()
        invoice.status = Invoice.StatusChoices.CANCELLED
        invoice.updated_by = request.user
        invoice.save()
        return Response({'message': 'Facture annulée.'})
