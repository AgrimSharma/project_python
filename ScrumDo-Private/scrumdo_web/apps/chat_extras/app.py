# This is a single place to hook up all the signal handling for all the chat based extras (slack, hipchat, flowdock) instead
# of each having their own handlers all firing all the time.

from django.apps import AppConfig



class ChatExtrasApp(AppConfig):
    name = 'apps.chat_extras'
    verbose_name = "ScrumDo Chat Extras"

    def ready(self):
        import signal_handlers
