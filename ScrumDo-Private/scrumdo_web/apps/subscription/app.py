from django.apps import AppConfig


class SubscriptionApp(AppConfig):
    name = 'apps.subscription'
    verbose_name = "ScrumDo Subscription App"

    def ready(self):
        from limit_handlers import initializeHandlers
        initializeHandlers()
        import tasks

