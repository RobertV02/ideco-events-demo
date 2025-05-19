# logs/apps.py
from django.apps import AppConfig

class LogsConfig(AppConfig):
    name = 'logs'

    def ready(self):
        # импортируем сигналы, чтобы post_save работал
        import logs.signals
