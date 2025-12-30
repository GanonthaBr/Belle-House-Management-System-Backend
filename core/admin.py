"""
Core admin configuration.

Customizes the Django admin site appearance.
"""

from django.contrib import admin


# Customize admin site
admin.site.site_header = "Belle House Administration"
admin.site.site_title = "Belle House Admin"
admin.site.index_title = "Bienvenue sur le panneau d'administration Belle House"
