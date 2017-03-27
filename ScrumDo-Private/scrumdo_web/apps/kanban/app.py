from django.apps import AppConfig


class KanbanApp(AppConfig):
    name = 'apps.kanban'
    verbose_name = "ScrumDo Kanban"

    def ready(self):
        import signal_handlers  # so the signal gets hooked up correctly.
