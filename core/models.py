"""
Core models for Belle House Backend.

This module contains abstract base models that provide common functionality
for all other models in the system:
- Soft delete capability
- Audit trail (created_at, updated_at, created_by, updated_by)
- Custom managers for filtering deleted records
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class ActiveManager(models.Manager):
    """
    Custom manager that filters out soft-deleted records by default.
    Use this for normal queries where you don't want to see deleted records.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """
    Manager that returns all records including soft-deleted ones.
    Use this when you need to access deleted records (e.g., in admin for restore).
    """
    def get_queryset(self):
        return super().get_queryset()


class BaseModel(models.Model):
    """
    Abstract base model that provides:
    - Timestamps (created_at, updated_at)
    - Audit fields (created_by, updated_by)
    - Soft delete (is_deleted, deleted_at, deleted_by)
    
    All models in the system should inherit from this class.
    """
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name="Créé par"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name="Modifié par"
    )
    
    # Soft delete fields
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Supprimé"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Supprimé le"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
        verbose_name="Supprimé par"
    )
    
    # Managers
    objects = ActiveManager()  # Default: only non-deleted records
    all_objects = AllObjectsManager()  # All records including deleted
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """
        Soft delete this record.
        Sets is_deleted=True and records deletion timestamp and user.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'updated_at'])
    
    def restore(self, user=None):
        """
        Restore a soft-deleted record.
        Clears deletion fields and optionally records who restored it.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        if user:
            self.updated_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'updated_by', 'updated_at'])
    
    def hard_delete(self):
        """
        Permanently delete this record from the database.
        Use with caution - this cannot be undone.
        """
        super().delete()


class TimeStampedModel(models.Model):
    """
    A lighter abstract model that only provides timestamps without soft delete.
    Use this for models where soft delete is not needed (e.g., log entries).
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )
    
    class Meta:
        abstract = True
