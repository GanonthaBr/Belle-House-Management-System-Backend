from django.apps import AppConfig


class MarketingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "marketing"
    verbose_name = "Marketing & Site Web"
    
    def ready(self):
        # Import signals to register handlers
        import marketing.signals  # noqa: F401
