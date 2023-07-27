from django.apps import AppConfig

# from django.utils.translation import ugettext_lazy as _

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    
    def ready(self):
        import bot.signals  # noqa 