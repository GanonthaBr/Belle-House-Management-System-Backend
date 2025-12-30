"""
Admin API Views for Clients models.

Staff-only CRUD endpoints for clients and projects.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import ClientProfile, ActiveProject, ProjectUpdate, AppPromotion
from .serializers import (
    ClientProfileSerializer, ClientCreateSerializer,
    ActiveProjectListSerializer, ActiveProjectDetailSerializer, ActiveProjectWriteSerializer,
    ProjectUpdateSerializer, ProjectUpdateWriteSerializer,
    AppPromotionSerializer, AppPromotionWriteSerializer
)

User = get_user_model()


class AdminClientViewSet(viewsets.ModelViewSet):
    """
    Admin client management.
    
    list: GET /api/admin/clients/
    retrieve: GET /api/admin/clients/{id}/
    create: POST /api/admin/clients/ (creates User + ClientProfile)
    update: PUT/PATCH /api/admin/clients/{id}/
    destroy: DELETE /api/admin/clients/{id}/ (soft delete profile)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone_number', 'address']
    ordering_fields = ['created_at', 'user__first_name', 'user__email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ClientProfile.objects.select_related('user').prefetch_related('projects').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        return ClientProfileSerializer
    
    def perform_destroy(self, instance):
        """Soft delete profile and deactivate user"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()
        # Also deactivate the user account
        instance.user.is_active = False
        instance.user.save()
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a deleted client.
        
        POST /api/admin/clients/{id}/reactivate/
        """
        # Override manager to get deleted clients
        client = ClientProfile.all_objects.get(pk=pk)
        client.is_deleted = False
        client.deleted_at = None
        client.deleted_by = None
        client.updated_by = request.user
        client.save()
        # Reactivate user
        client.user.is_active = True
        client.user.save()
        return Response({'message': 'Client réactivé.'})
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Reset client password and send email.
        
        POST /api/admin/clients/{id}/reset_password/
        """
        client = self.get_object()
        # Generate random password
        import secrets
        new_password = secrets.token_urlsafe(12)
        client.user.set_password(new_password)
        client.user.save()
        # TODO: Send email with new password
        return Response({
            'message': 'Mot de passe réinitialisé.',
            'temporary_password': new_password  # In production, only send via email
        })


class AdminActiveProjectViewSet(viewsets.ModelViewSet):
    """
    Admin project management.
    
    list: GET /api/admin/projects/
    retrieve: GET /api/admin/projects/{id}/
    create: POST /api/admin/projects/
    update: PUT/PATCH /api/admin/projects/{id}/
    destroy: DELETE /api/admin/projects/{id}/ (soft delete)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['client', 'current_phase']
    search_fields = ['name', 'description', 'location', 'client__user__first_name', 'client__user__last_name']
    ordering_fields = ['created_at', 'start_date', 'name', 'total_contract_value']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ActiveProject.objects.select_related('client', 'client__user').prefetch_related('updates', 'invoices').all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ActiveProjectWriteSerializer
        if self.action == 'retrieve':
            return ActiveProjectDetailSerializer
        return ActiveProjectListSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()
    
    @action(detail=True, methods=['post'])
    def advance_phase(self, request, pk=None):
        """
        Advance project to next phase.
        
        POST /api/admin/projects/{id}/advance_phase/
        """
        project = self.get_object()
        phases = [choice[0] for choice in ActiveProject.Phase.choices]
        current_index = phases.index(project.current_phase)
        
        if current_index < len(phases) - 1:
            project.current_phase = phases[current_index + 1]
            project.updated_by = request.user
            project.save()
            return Response({
                'message': f'Projet avancé à la phase: {project.get_current_phase_display()}'
            })
        return Response(
            {'error': 'Le projet est déjà à la dernière phase.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def add_update(self, request, pk=None):
        """
        Add an update to the project.
        
        POST /api/admin/projects/{id}/add_update/
        {
            "title": "Update title",
            "description": "Update description",
            "images": ["url1", "url2"]  // optional
        }
        """
        project = self.get_object()
        serializer = ProjectUpdateWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                project=project,
                created_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProjectUpdateViewSet(viewsets.ModelViewSet):
    """
    Admin project update management.
    
    CRUD for project updates at /api/admin/project-updates/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project']
    search_fields = ['title', 'description', 'project__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ProjectUpdate.objects.select_related('project', 'project__client').all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectUpdateWriteSerializer
        return ProjectUpdateSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class AdminPromotionViewSet(viewsets.ModelViewSet):
    """
    Admin promotion management.
    
    CRUD for app promotions at /api/admin/promotions/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at', 'title']
    ordering = ['order']
    
    def get_queryset(self):
        return AppPromotion.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AppPromotionWriteSerializer
        return AppPromotionSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()
