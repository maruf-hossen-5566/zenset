from django.apps import AppConfig


class LikeAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "like_app"

    def ready(self):
        from . import signals
