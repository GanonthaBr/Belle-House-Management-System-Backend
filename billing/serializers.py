"""
Serializers for Billing API.

Used by both mobile app (read-only) and admin (full CRUD).
"""

from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items."""
    
    total_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'description', 'quantity', 'unit_price',
            'total_price', 'order'
        ]


class InvoiceItemWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating invoice items."""
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'order']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer for invoice list view (lightweight)."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    payment_mode_display = serializers.CharField(source='get_payment_mode_display', read_only=True)
    total_ttc = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    net_to_pay = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_type_display', 'subject', 'status', 'status_display',
            'issue_date', 'due_date', 'total_ttc', 'net_to_pay',
            'payment_mode', 'payment_mode_display',
            'project', 'project_name', 'client_name'
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for invoice detail view (full data with items)."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    payment_mode_display = serializers.CharField(source='get_payment_mode_display', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    
    # Computed fields
    subtotal = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_ttc = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    net_to_pay = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_type_display', 'subject', 'status', 'status_display',
            'issue_date', 'due_date',
            'tax_percentage', 'advance_payment',
            'payment_mode', 'payment_mode_display',
            # Client snapshot
            'client_name', 'client_address', 'client_phone',
            # Computed
            'subtotal', 'tax_amount', 'total_ttc', 'net_to_pay',
            # Relations
            'project', 'project_name', 'items',
            # Notes
            'notes',
            # Timestamps
            'created_at', 'updated_at'
        ]


class InvoiceWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating invoices (admin use)."""
    
    items = InvoiceItemWriteSerializer(many=True, required=False)
    
    class Meta:
        model = Invoice
        fields = [
            'project', 'invoice_type', 'subject', 'status',
            'issue_date', 'due_date',
            'tax_percentage', 'advance_payment', 'payment_mode',
            'client_name', 'client_address', 'client_phone',
            'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            # Remove existing items and create new ones
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
        
        return instance
