import requests

# отключаем InsecureRequestWarning
requests.packages.urllib3.disable_warnings()

class IdecoClient:
    def __init__(self, ip, port='8443', user='', password='', rest_path='/'):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.rest_path = rest_path

        self.base_url = f'https://{self.ip}:{self.port}'
        self.session = requests.Session()
        self.session.verify = False
        self.logged = False

        self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def login(self):
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
        if not self.logged:
            return
        url = f'{self.base_url}/web/auth/login'
        resp = self.session.delete(url)
        resp.raise_for_status()
        print("Выход выполнен")
        self.logged = False

    def _get(self, path):
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
        # тут возвращается список словарей с полем "id", "title", "values"...
        return self._get('/aliases/lists/addresses')

    def get_auth_sessions(self):
        return self._get('/monitor_backend/auth_sessions')

    def find_blocklist(self):
        lists = self.get_ip_address_lists()
        if not isinstance(lists, list):
            raise RuntimeError(f"Ожидался список, получили {type(lists)}")
        for entry in lists:
            if entry.get("title") == 'ip для блокировки':
                return entry.get("id"), entry
        raise RuntimeError("Список для блокировки не найден")

    def block_ip(self, address):
        list_id, data = self.find_blocklist()
        if address in data.get('values', []):
            print(f'Адрес {address} уже заблокирован')
            return
        payload = data.copy()
        payload['values'] = payload.get('values', []) + [address]
        payload.pop('type', None)
        # вот правильный путь к ресурсу
        self._put(f'/aliases/lists/addresses/{list_id}', payload)
        print(f'Адрес {address} заблокирован')

    def unblock_ip(self, address):
        list_id, data = self.find_blocklist()
        if address not in data.get('values', []):
            print(f'Адрес {address} не был заблокирован')
            return
        payload = data.copy()
        vals = payload.get('values', [])
        vals.remove(address)
        payload['values'] = vals
        payload.pop('type', None)
        self._put(f'/aliases/lists/addresses/{list_id}', payload)
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
