from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    defaul_app_config = 'applications.store.apps.StoreConfig'

    name = 'applications.store'

    def ready(self):
        import applications.store.signals