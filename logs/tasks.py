# logs/tasks.py
import requests, os
from celery import shared_task
from django.conf import settings
from requests.exceptions import HTTPError

@shared_task
def block_ip(ip):
    """
    Логин → alias IP → правило DROP.
    При ошибке выводит traceback в логи Celery.
    """
    url     = 'https://192.168.56.10:8443'
    login   = 'admin'
    passwd  = 'Robertsyuzililit2+'

    with requests.Session() as s:
        s.verify = False                 # самоподписанный сертификат

        # 1. Авторизация
        auth_payload = {
            "login": login,
            "password": passwd,
            "recaptcha": "",
            "rest_path": "/"
        }
        r = s.post(f"{url}/web/auth/login", json=auth_payload, timeout=10)
        r.raise_for_status()             # 200 ⇾ вошли, куки сохранены

        # 2. Создаём alias IP
        alias_payload = {
            "title": f"IRP_{ip}",
            "comment": "auto-ban from IRP",
            "value": ip
        }
        r = s.post(f"{url}/aliases/ip_addresses",
                   json=alias_payload, timeout=10)
        r.raise_for_status()
        alias_id = r.json().get("id")

        # 3. Добавляем DROP-правило
        rule_payload = {
            "action": "drop",
            "comment": f"IRP-auto-ban {ip}",
            "destination_addresses": [alias_id],
            "destination_ports": ["any"],
            "incoming_interface": "any",
            "outgoing_interface": "any",
            "protocol": "any",
            "source_addresses": ["any"],
            "timetable": ["any"],
            "enabled": True
        }
        r = s.post(f"{url}/firewall/rules/forward",
                   json=rule_payload, timeout=10)
        r.raise_for_status()

        print(f"[IRP] IP {ip} заблокирован (ID alias {alias_id})")

