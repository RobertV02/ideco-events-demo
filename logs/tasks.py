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
    Celery: баним IP по событию, добавляя его в список.
    """
    try:
        client = IdecoClient(
            ip='192.168.56.10',
            port='8443',
            user='admin',
            password='Robertsyuzililit2+',
            rest_path='/'
        )
        client.block_ip(address)
    except Exception as e:
        print(f"[IRP] Ошибка при бане {address}: {e}")