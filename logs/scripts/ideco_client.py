import requests
import urllib3

# Отключаем предупреждения по сертификату
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IdecoClient:
    def __init__(self, ip, port='8443', user='', password='', rest_path='/'):
        # сохраняем параметры
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.rest_path = rest_path

        # базовый URL и сессия
        self.base_url = f'https://{self.ip}:{self.port}'
        self.session = requests.Session()
        self.session.verify = False
        self.logged = False

        # сразу логинимся
        self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def login(self):
        """Авторизация и получение cookie."""
        url = f'{self.base_url}/web/auth/login'
        payload = {
            "login": self.user,
            "password": self.password,
            "rest_path": self.rest_path
        }
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        print("Успешная авторизация")
        self.logged = True

    def logout(self):
        """Удаление сессии."""
        if not self.logged:
            return
        url = f'{self.base_url}/web/auth/login'
        resp = self.session.delete(url)
        resp.raise_for_status()
        print("Выход выполнен")
        self.logged = False

    def _get(self, path):
        """Обёртка GET-запроса."""
        if not self.logged:
            self.login()
        url = f'{self.base_url}{path}'
        resp = self.session.get(url)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            print("Ошибка парсинга JSON")
            return None

    def _put(self, path, data):
        """Обёртка PUT-запроса."""
        if not self.logged:
            self.login()
        url = f'{self.base_url}{path}'
        resp = self.session.put(url, json=data)
        resp.raise_for_status()
        return resp

    def get_users_list(self):
        return self._get('/user_backend/users')

    def get_rules_list(self):
        return self._get('/firewall/rules/forward')

    def get_ip_address_lists(self):
        return self._get('/aliases/lists/addresses')

    def get_auth_sessions(self):
        return self._get('/monitor_backend/auth_sessions')

    def find_blocklist(self):
        """
        Ищем список IP-адресов для блокировки.
        Ожидаем список dict'ов:
        [
          { "id": "...", "title": "ip для блокировки", "values": [...], ... },
          ...
        ]
        """
        lists = self.get_ip_address_lists()
        if not isinstance(lists, list):
            raise RuntimeError("Ожидался список, получили не список")
        for entry in lists:
            if entry.get("title") == 'ip для блокировки':
                list_id = entry.get("id")
                return list_id, entry
        raise RuntimeError("Список для блокировки не найден")

    def block_ip(self, address):
        """Добавляем IP в блок-лист."""
        list_id, data = self.find_blocklist()
        values = data.get('values', [])
        if address in values:
            print(f'Адрес {address} уже заблокирован')
            return
        values.append(address)
        self._put(f'/aliases/ip_address_lists/{list_id}', data)
        print(f'Адрес {address} заблокирован')

    def unblock_ip(self, address):
        """Удаляем IP из блок-листа."""
        list_id, data = self.find_blocklist()
        values = data.get('values', [])
        if address not in values:
            print(f'Адрес {address} не был заблокирован')
            return
        values.remove(address)
        self._put(f'/aliases/ip_address_lists/{list_id}', data)
        print(f'Адрес {address} разблокирован')

    def find_rule_for_block(self):
        for rule in self.get_rules_list():
            if rule.get("id") == 500:
                return rule
        raise RuntimeError("Правило блокировки не найдено")

    def get_blocked_users(self):
        rule = self.find_rule_for_block()
        users = self.get_users_list()
        blocked = []
        for src in rule.get('source_addresses', []):
            uid = src.replace("user.id.", "")
            for u in users:
                if str(u.get("id")) == uid:
                    blocked.append(u.get("login"))
        return blocked

    def block_user(self, username):
        if username in self.get_blocked_users():
            print(f'Пользователь {username} уже заблокирован')
            return
        rule = self.find_rule_for_block()
        uid = next(u['id'] for u in self.get_users_list() if u['login'] == username)
        rule['source_addresses'].append(f"user.id.{uid}")
        rule_id = rule.pop('id')
        self._put(f'/firewall/rules/forward/{rule_id}', rule)
        print(f'Пользователь {username} заблокирован')

    def unblock_user(self, username):
        if username not in self.get_blocked_users():
            print(f'Пользователь {username} не был заблокирован')
            return
        rule = self.find_rule_for_block()
        uid = next(u['id'] for u in self.get_users_list() if u['login'] == username)
        rule['source_addresses'].remove(f"user.id.{uid}")
        rule_id = rule.pop('id')
        self._put(f'/firewall/rules/forward/{rule_id}', rule)
        print(f'Пользователь {username} разблокирован')
