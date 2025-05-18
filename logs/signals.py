# logs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from .tasks import block_ip

@receiver(post_save, sender=Event)
def trigger_block_ip(sender, instance, created, **kwargs):
    """
    При сохранении Event с action 'Bad TLS Certificate'
    отправляем задачу блокировки IP
    """
    if created and instance.action == "Bad TLS Certificate":
        block_ip.delay(instance.src_ip)
