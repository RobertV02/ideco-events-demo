# logs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from .block_detector import detect_and_block

@receiver(post_save, sender=Event)
def on_event_saved(sender, instance, created, **kwargs):
    if created:
        # весь парсинг и решение о блокировке — в отдельном модуле
        detect_and_block(instance)
