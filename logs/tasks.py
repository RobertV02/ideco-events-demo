# logs/tasks.py
from celery import shared_task
from .scripts.adapter import run as adapter_run
from .scripts.cleaner import run as cleaner_run
from .scripts.normalizer import run as normalizer_run
import logging
import requests, os
from requests.exceptions import HTTPError
from .scripts.ideco_client import IdecoClient

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
def block_ip(address: str):
    """
    Celery-таск: по событию баним IP, дописывая его в заранее созданный IP-список.
    """
    client = IdecoClient()
    try:
        client.block_ip(address)
    except Exception as e:
        # никогда не падаем, а логируем
        print(f"[IRP] Ошибка при бане {address}: {e}")