from django.apps import AppConfig


class ClientsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clients"
    verbose_name = "Portail Clients"
    
    def ready(self):
        # Import signals to register handlers
        import clients.signals  # noqa: F401
