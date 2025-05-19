# файл: logs/scripts/ideco_client.py

import os
import requests
from django.conf import settings

class IdecoClient:
    """
    Клиент для работы с REST-API Ideco UTM:
     - логинимся,
     - получаем списки IP-адресов,
     - находим нужный блок-лист по title,
     - добавляем туда новые адреса.
    """

    def __init__(self):
        self.base_url = '192.168.56.10'
        self.login    = 'admin'
        self.password = 'Robertsyuzililit2+'
        self.session  = requests.Session()
        # если у вас самоподписанный сертификат:
        self.session.verify = False
        self._logged_in = False

    def login_if_needed(self):
        """Выполняем POST /web/auth/login один раз за сессию."""
        if self._logged_in:
            return
        url = f"{self.base_url}/web/auth/login"
        payload = {
            "login":     self.login,
            "password":  self.password,
            "rest_path": "/"
        }
        r = self.session.post(url, json=payload, timeout=10)
        r.raise_for_status()
        self._logged_in = True

    def get_ip_address_lists(self):
        """GET /aliases/ip_address_lists → возвращает dict id→объект или list."""
        self.login_if_needed()
        url = f"{self.base_url}/aliases/ip_address_lists"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def find_blocklist(self, title: str = "ip для блокировки"):
        """
        Ищет в полученных списках тот, у которого 'title' == нужному.
        Возвращает (id, data) или бросает ValueError.
        """
        lists = self.get_ip_address_lists()
        # может быть в формате {id: {…}, …} или [{…}, …]
        if isinstance(lists, dict):
            for lid, data in lists.items():
                if data.get("title") == title:
                    return lid, data
        else:
            for entry in lists:
                if entry.get("title") == title:
                    return entry["id"], entry
        raise ValueError(f"Blocklist '{title}' not found")

    def put_to_endpoint(self, url: str, data: dict):
        """Универсальный PUT → возвращает JSON или бросает ошибку."""
        r = self.session.put(url, json=data, timeout=10)
        r.raise_for_status()
        return r.json()

    def block_ip(self, address: str):
        """
        Добавляет address в values нужного списка.
        Если уже есть — ничего не делает.
        """
        self.login_if_needed()
        blocklist_id, data = self.find_blocklist()
        values = data.get("values", [])
        if address in values:
            print(f"[Ideco] {address} уже в списке блокировки")
            return
        values.append(address)
        # API не любит лишних полей:
        data = {
            "title":   data["title"],
            "comment": f"auto-ban {address}",
            "values":  values
        }
        url = f"{self.base_url}/aliases/ip_address_lists/{blocklist_id}"
        self.put_to_endpoint(url, data)
        print(f"[Ideco] {address} добавлен в блоклист {blocklist_id}")
