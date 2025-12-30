"""
Utility functions for Belle House Backend.

This module contains reusable helper functions used across the application.
"""

import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


def compress_image(image_field, max_size=(1200, 1200), quality=85):
    """
    Compress and resize an image while maintaining aspect ratio.
    
    Args:
        image_field: Django ImageField instance
        max_size: Tuple of (max_width, max_height)
        quality: JPEG quality (1-100)
    
    Returns:
        ContentFile with compressed image or None if no compression needed
    """
    if not image_field:
        return None
    
    try:
        # Open the image
        img = Image.open(image_field)
        
        # Get original format
        original_format = img.format or 'JPEG'
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'P') and original_format == 'JPEG':
            img = img.convert('RGB')
        
        # Check if resize is needed
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to buffer
        buffer = BytesIO()
        
        # Determine format and extension
        if original_format.upper() in ('PNG', 'GIF'):
            # Keep PNG/GIF format for transparency
            save_format = original_format.upper()
            if save_format == 'PNG':
                img.save(buffer, format='PNG', optimize=True)
            else:
                img.save(buffer, format='GIF', optimize=True)
        else:
            # Convert everything else to JPEG
            save_format = 'JPEG'
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        buffer.seek(0)
        
        # Generate new filename
        name = os.path.splitext(os.path.basename(image_field.name))[0]
        ext = 'jpg' if save_format == 'JPEG' else save_format.lower()
        new_name = f"{name}_compressed.{ext}"
        
        return ContentFile(buffer.read(), name=new_name)
    
    except Exception as e:
        # Log error but don't crash
        print(f"Image compression error: {e}")
        return None


def format_currency(amount, currency='FCFA'):
    """
    Format a decimal amount as currency string.
    
    Args:
        amount: Decimal or float value
        currency: Currency symbol (default: FCFA)
    
    Returns:
        Formatted string like "1,500,000 FCFA"
    """
    if amount is None:
        return f"0 {currency}"
    return f"{amount:,.0f} {currency}"


def generate_reference(prefix, model_class, field_name='reference'):
    """
    Generate a unique reference number.
    
    Args:
        prefix: String prefix (e.g., 'BH', 'INV')
        model_class: Django model class to check for existing references
        field_name: Name of the reference field
    
    Returns:
        String like "BH/2025/001"
    """
    from django.utils import timezone
    
    current_year = timezone.now().year
    full_prefix = f"{prefix}/{current_year}/"
    
    # Find last reference with this prefix
    filter_kwargs = {f"{field_name}__startswith": full_prefix}
    last_obj = model_class.objects.filter(**filter_kwargs).order_by(f'-{field_name}').first()
    
    if last_obj:
        try:
            last_num = int(getattr(last_obj, field_name).split('/')[-1])
            new_num = last_num + 1
        except (ValueError, IndexError):
            new_num = 1
    else:
        new_num = 1
    
    return f"{full_prefix}{new_num:03d}"
