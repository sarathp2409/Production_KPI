from django.apps import AppConfig


class DefaultDataHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'handler_default_data'
