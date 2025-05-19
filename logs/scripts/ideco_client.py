import requests

class IdecoClient:
    def __init__(self, ip='', port='8443', user='', password='', rest_path='/'):
        self.base_url = 'https://192.168.56.10:8443'
        self.login    = 'admin'
        self.password = 'Robertsyuzililit2+'
        self.rest_path = rest_path

        self.session = requests.Session()
        self.session.verify = False
        self.logged = False

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def get_from_endpoint(self, url):
        try:
            response = self.session.get(url=url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    def post_to_endpoint(self, url, obj_dict):
        try:
            response = self.session.post(url=url, json=obj_dict)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    def put_to_endpoint(self, url, obj_dict):
        try:
            response = self.session.put(url=url, json=obj_dict)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(response.content)
            return None

    def login(self):
        url = f'{self.base_url}/web/auth/login'
        data = {
            "login": self.user,
            "password": self.password,
            "rest_path": self.rest_path
        }
        response = self.post_to_endpoint(url, data)
        if response is not None:
            print("Успешная авторизация")
            self.logged = True
        else:
            raise RuntimeError("Ошибка авторизации")

    def logout(self):
        if self.logged:
            url = f'{self.base_url}/web/auth/login'
            response = self.session.delete(url)
            response.raise_for_status()
            self.logged = False
            print("Выход выполнен")

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

    def check_status_ip(self, address):
        _id, info = self.find_blocklist()
        return address in info.get('values', [])

    def block_ip(self, address):
        """
        Блокирует IP-адрес путём добавления в список IP-адресов
        """
        if self.check_status_ip(address):
            print(f"Адрес {address} уже заблокирован")
            return
        blocklist_id, data = self.find_blocklist()
        data['values'].append(address)
        data.pop('type', None)
        url = f'{self.base_url}/aliases/ip_address_lists/{blocklist_id}'
        response = self.put_to_endpoint(url, data)
        if response is not None:
            print(f"Адрес {address} заблокирован")
        else:
            print(f"Не удалось заблокировать адрес {address}")

    def unblock_ip(self, address):
        """
        Разблокирует IP-адрес путём удаления из списка IP-адресов
        """
        if not self.check_status_ip(address):
            print(f"Адрес {address} не блокируется")
            return
        blocklist_id, data = self.find_blocklist()
        data['values'].remove(address)
        data.pop('type', None)
        url = f'{self.base_url}/aliases/ip_address_lists/{blocklist_id}'
        response = self.put_to_endpoint(url, data)
        if response is not None:
            print(f"Адрес {address} разблокирован")
        else:
            print(f"Не удалось разблокировать адрес {address}")
