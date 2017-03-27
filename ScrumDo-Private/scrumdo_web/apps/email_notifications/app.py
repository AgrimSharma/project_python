from django.apps import AppConfig


class EmailNotificationApp(AppConfig):
    name = 'apps.email_notifications'
    verbose_name = "ScrumDo Email Notifications App"

    def ready(self):
        import apps.email_notifications.signal_handlers
