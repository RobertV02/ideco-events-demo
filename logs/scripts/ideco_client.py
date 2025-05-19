import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
# Отключаем предупреждения про самоподписанный сертификат
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class IdecoClient:
    """
    Клиент для работы с REST-API Ideco UTM:
      - логинимся,
      - получаем списки IP-адресов,
      - находим нужный блок-лист по title,
      - добавляем или удаляем туда адреса.
    """
    def __init__(self):
        self.base_url = 'https://192.168.56.10:8443'
        self.user     = 'admin'
        self.password = 'Robertsyuzililit2+'
        self.rest_path = '/'

        self.session = requests.Session()
        self.session.verify = False
        self._logged_in = False

    def login(self):
        url = f"{self.base_url}{self.rest_path}/web/auth/login"
        payload = {
            "login": self.user,
            "password": self.password,
            "rest_path": "/"
        }
        r = self.session.post(url, json=payload)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Ошибка авторизации: {e}")
        self._logged_in = True
        print("Успешная авторизация")

    def logout(self):
        if not self._logged_in:
            return
        url = f"{self.base_url}{self.rest_path}/web/auth/login"
        r = self.session.delete(url)
        r.raise_for_status()
        self._logged_in = False
        print("Выход выполнен")
        
    def parse_json(self, response):
        try:
            response = response.json()
            return response
        except:
            print('Ошибка парсинга JSON')
            
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

    def put_to_endpoint(self, path, data):
        if not self._logged_in:
            self.login()
        url = f"{self.base_url}{self.rest_path}{path}"
        r = self.session.put(url, json=data)
        try:
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(r.content)
            return None

    def get_ip_address_lists(self):
        """Возвращает словарь всех alias-списков: id → info"""
        url = f'{self.base_url}/aliases/ip_address_lists'
        return self.get_from_endpoint(url)

    def find_blocklist(self):
        """
        Возвращает список для блокировки IP-адресов

        :return:
            Возвращает словарь со списком для блокировки по IP-адресу
        """
        for list in self.get_ip_address_lists().items():
            if list[1]["title"] == 'List_for_test_api':
                return list
        print("Список для блокировки не найден")
        return self.logout()

    def check_status_ip(self, address):
        """True, если адрес уже в списке"""
        blocklist_id, info = self.find_blocklist()
        if not info:
            return False
        return address in info.get('values', [])

    def block_ip(self, address):
        """
        Добавляет IP-адрес в alias-список.
        """
        # Проверяем, не заблокирован ли уже
        if self.check_status_ip(address):
            print(f"Адрес {address} уже заблокирован")
            return
        # Находим список
        blocklist_id, data = self.find_blocklist()
        if not blocklist_id:
            raise RuntimeError("Список для блокировки не найден")
        # Добавляем и отправляем
        data['values'].append(address)
        data.pop('type', None)
        path = f"/aliases/ip_address_lists/{blocklist_id}"
        result = self.put_to_endpoint(path, data)
        if result is not None:
            print(f"Адрес {address} заблокирован")
        else:
            print(f"Не удалось заблокировать адрес {address}")

    def unblock_ip(self, address):
        """
        Удаляет IP-адрес из alias-списка.
        """
        if not self.check_status_ip(address):
            print(f"Адрес {address} не блокируется")
            return
        blocklist_id, data = self.find_blocklist()
        data['values'].remove(address)
        data.pop('type', None)
        path = f"/aliases/ip_address_lists/{blocklist_id}"
        result = self.put_to_endpoint(path, data)
        if result is not None:
            print(f"Адрес {address} разблокирован")
        else:
            print(f"Не удалось разблокировать адрес {address}")
