from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "billing"
    verbose_name = "Facturation"
    
    def ready(self):
        # Import signals to register handlers
        import billing.signals  # noqa: F401
