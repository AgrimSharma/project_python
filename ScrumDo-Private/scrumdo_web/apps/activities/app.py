from django.apps import AppConfig


class ActivitiesApp(AppConfig):
    name = 'apps.activities'
    verbose_name = "ScrumDo Activities App"

    def ready(self):
        import signal_handlers
