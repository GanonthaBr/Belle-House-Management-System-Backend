"""
Views for Clients API.

Mobile app endpoints for authenticated clients.
"""

from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import ClientProfile, ActiveProject, ProjectUpdate, AppPromotion
from .serializers import (
    ClientProfileSerializer, ClientProfileUpdateSerializer,
    ActiveProjectListSerializer, ActiveProjectDetailSerializer,
    ProjectUpdateSerializer, AppPromotionSerializer
)
from billing.models import Invoice
from billing.serializers import InvoiceListSerializer, InvoiceDetailSerializer


# =============================================================================
# MOBILE APP VIEWS (Client Role)
# =============================================================================

class ClientProfileView(generics.RetrieveUpdateAPIView):
    """
    Client profile endpoint.
    
    GET /api/app/profile/ - Get current client's profile
    PUT/PATCH /api/app/profile/ - Update profile
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(ClientProfile, user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ClientProfileUpdateSerializer
        return ClientProfileSerializer


class MyProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Client's active projects endpoint.
    
    list: GET /api/app/my-projects/
    retrieve: GET /api/app/my-projects/{id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client_profile = self.request.user.client_profile
            return ActiveProject.objects.filter(client=client_profile)
        except ClientProfile.DoesNotExist:
            return ActiveProject.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ActiveProjectDetailSerializer
        return ActiveProjectListSerializer
    
    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        """
        Get updates for a specific project.
        
        GET /api/app/my-projects/{id}/updates/
        """
        project = self.get_object()
        updates = project.updates.all()
        serializer = ProjectUpdateSerializer(updates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """
        Get invoices for a specific project.
        
        GET /api/app/my-projects/{id}/invoices/
        """
        project = self.get_object()
        invoices = project.invoices.all()
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


class MyInvoiceDetailView(generics.RetrieveAPIView):
    """
    Client's invoice detail endpoint.
    
    GET /api/app/invoices/{id}/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceDetailSerializer
    
    def get_queryset(self):
        try:
            client_profile = self.request.user.client_profile
            return Invoice.objects.filter(project__client=client_profile)
        except ClientProfile.DoesNotExist:
            return Invoice.objects.none()


class AppPromotionListView(generics.ListAPIView):
    """
    Active promotions for mobile app.
    
    GET /api/app/promotions/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AppPromotionSerializer
    
    def get_queryset(self):
        return AppPromotion.objects.filter(is_active=True).order_by('order')
