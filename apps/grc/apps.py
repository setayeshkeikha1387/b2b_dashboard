from django.apps import AppConfig


class GrcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.grc"
    label = "grc"
    verbose_name = "Risk & Control"

    def ready(self) -> None:
        from apps.grc import signals  # noqa: F401
