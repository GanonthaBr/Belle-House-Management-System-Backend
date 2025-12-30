from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "leads"
    verbose_name = "Gestion des Leads"
    
    def ready(self):
        # Import signals to register handlers
        import leads.signals  # noqa: F401
