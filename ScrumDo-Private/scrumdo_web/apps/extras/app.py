from django.apps import AppConfig


class ExtrasApp(AppConfig):
    name = 'apps.extras'
    verbose_name = "ScrumDo Extras"

    def ready(self):
        import tasks  # so the signal gets hooked up correctly.
