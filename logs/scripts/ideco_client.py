import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

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
        self.rest_path = '/api/'

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

    def get_from_endpoint(self, path):
        if not self._logged_in:
            self.login()
        url = f"{self.base_url}{self.rest_path}{path}"
        r = self.session.get(url)
        try:
            r.raise_for_status()
            return r.json()
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
        return self.get_from_endpoint('/aliases/ip_address_lists')

    def find_blocklist(self, title='ip для блокировки'):
        """Ищет alias-список по заголовку и возвращает (id, info)"""
        lists = self.get_ip_address_lists()
        if not lists:
            print("Не получили список alias-списков")
            return None, None
        for list_id, info in lists.items():
            if info.get('title') == title:
                return list_id, info
        print(f"Список '{title}' не найден")
        return None, None

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
