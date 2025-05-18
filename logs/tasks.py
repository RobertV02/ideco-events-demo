# logs/tasks.py
from celery import shared_task
from .scripts.adapter import run as adapter_run
from .scripts.cleaner import run as cleaner_run
from .scripts.normalizer import run as normalizer_run
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_event_pipeline():
    """
    Последовательный запуск конвейера обработки событий:
    adapter -> cleaner -> normalizer
    """
    events = adapter_run()
    events = cleaner_run(events)
    return normalizer_run(events)

@shared_task
def block_ip(ip_address):
    """
    Заготовка задачи блокировки IP-адреса (позже через Jenkins).
    """
    logger.info(f"Блокировка IP-адреса: {ip_address}")
    # Здесь можно добавить сохранение в базу BlockedIP или вызов Jenkins
