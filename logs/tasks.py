# logs/tasks.py
from celery import shared_task
from .scripts.adapter import run as adapter_run
from .scripts.cleaner import run as cleaner_run
from .scripts.normalizer import run as normalizer_run
import logging
import requests, os
from requests.exceptions import HTTPError

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


@shared_task(bind=True, name="logs.tasks.block_ip")
def block_ip(self, ip: str):
    """
    Пытается залогиниться, создать alias и правило drop для IP.
    При ошибках логирует их и завершает задачу без падения.
    """
    url     = 'https://192.168.56.10:8443'
    login   = 'admin'
    passwd  = 'Robertsyuzililit2+'

    session = requests.Session()
    session.verify = False  # отключаем проверку SSL (для self-signed)
    try:
        # 1. Авторизация
        auth_payload = {
            "login":     login,
            "password":  passwd,
            "recaptcha": "",
            "rest_path": "/"
        }
        resp = session.post(f"{url}/web/auth/login", json=auth_payload, timeout=10)
        resp.raise_for_status()
    except HTTPError as e:
        # логируем HTTP-ошибку (542 и т.д.) и выходим
        self.update_state(state="FAILURE", meta={"exc": str(e), "step": "login"})
        print(f"[block_ip] Не удалось залогиниться: {e}")
        return f"login error: {e}"
    except RequestException as e:
        self.update_state(state="FAILURE", meta={"exc": str(e), "step": "login"})
        print(f"[block_ip] Ошибка сети при логине: {e}")
        return f"network error: {e}"

    try:
        # 2. Создаём alias IP
        alias_payload = {
            "title":   f"IRP_{ip}",
            "comment": "auto-ban from IRP",
            "value":   ip
        }
        resp = session.post(f"{url}/aliases/ip_addresses", json=alias_payload, timeout=10)
        resp.raise_for_status()
        alias_id = resp.json().get("id")
    except Exception as e:
        print(f"[block_ip] Не удалось создать alias: {e}")
        return f"alias error: {e}"

    try:
        # 3. Добавляем правило DROP
        rule_payload = {
            "action":                "drop",
            "comment":               f"IRP-auto-ban {ip}",
            "destination_addresses": [alias_id],
            "destination_ports":     ["any"],
            "incoming_interface":    "any",
            "outgoing_interface":    "any",
            "protocol":              "any",
            "source_addresses":      ["any"],
            "timetable":             ["any"],
            "enabled":               True
        }
        resp = session.post(f"{url}/firewall/rules/forward", json=rule_payload, timeout=10)
        resp.raise_for_status()
        print(f"[block_ip] IP {ip} заблокирован (alias {alias_id})")
        return f"blocked {ip}"
    except Exception as e:
        print(f"[block_ip] Не удалось добавить правило: {e}")
        return f"rule error: {e}"
