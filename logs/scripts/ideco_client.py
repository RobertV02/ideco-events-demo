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
        self.base_url = 'https://192.168.56.10:8443'
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
        
    def get_from_endpoint(self, url):
        """
        Отправляет запрос на указанный URL методом GET

        :parameters:
            url
                URL для отправки

        :return:
            Возвращает словарь
        """
        try:
            response = self.session.get(url = url)
            response.raise_for_status()
            return self.parse_json(response)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        
    def get_ip_address_lists(self):
        url = f'{self.base_url}/aliases/ip_address_lists'
        return self.get_from_endpoint(url)

    def find_blocklist(self):
        lists = self.get_ip_address_lists()
        for list_id, info in lists.items():
            if info.get("title") == 'ip для блокировки':
                return list_id, info
        print("Список для блокировки не найден")
        self.logout()

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
