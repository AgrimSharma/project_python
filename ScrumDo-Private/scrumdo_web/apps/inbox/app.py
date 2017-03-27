from django.apps import AppConfig


class ScrumDoInboxApp(AppConfig):
    name = 'apps.inbox'
    verbose_name = "ScrumDo Inbox App"

    def ready(self):
        import signal_handlers
