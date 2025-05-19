import requests
import json
requests.packages.urllib3.disable_warnings()
import requests


class IdecoClient:
    def __init__(self, ip = '', port = '8443', user = '', password = '', rest_path = '/'):
        self.ip = '192.168.56.10'
        self.port = '8443'
        self.user = 'admin'
        self.password = 'Robertsyuzililit2+'
        self.rest_path = rest_path

        self.base_url = f'https://{ip}:{port}'
        self.session = requests.Session()
        self.session.verify = False
        self.logged = False

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()


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

    def post_to_endpoint(self, url, obj_dict):
        """
        Отправляет запрос на указанный URL методом POST

        :parameters:
            url
                URL для отправки
            obj_dict
                Словарь для отправки

        :return:
            Возвращает статус ответа
        """
        try:
            response = self.session.post(url = url, json = obj_dict)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    def put_to_endpoint(self, url, obj_dict):
        """
        Отправляет запрос на указанный URL методом PUT

        :parameters:
            url
                URL для отправки
            obj_dict
                Словарь для отправки

        :return:
            Возвращает статус ответа
        """
        try:
            response = self.session.put(url = url, json = obj_dict)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(response.content)
            return None

    def parse_json(self, response):
        try:
            response = response.json()
            return response
        except:
            print('Ошибка парсинга JSON')


    def login(self):
        """
        Выполняет авторизацию, меняет статус авторизации "self.logged"

        """
        url = 'https://192.168.56.10:8433/web/auth/login'
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
        """
        Выполняет разавторизацию, меняет статус авторизации "self.logged"
        
        """
        if self.logged:
            url = 'https://192.168.56.10:8433/web/auth/login'
            response = self.session.delete(url)
            if response.status_code == 200:
                self.logged = False
                print("Выход выполнен")
            response.raise_for_status()


    def get_users_list(self):
        """
        Возвращает список пользователей

        :return:
            Возвращает список словарей со всеми пользователями
        """
        url = 'https://192.168.56.10:8433/user_backend/users'
        return self.get_from_endpoint(url)

    def get_rules_list(self):
        """
        Возвращает список правил

        :return:
            Возвращает список словарей со всеми правилами политики
        """
        url = 'https://192.168.56.10:8433/firewall/rules/forward'
        return self.get_from_endpoint(url)

    def get_ip_address_lists(self):
        """
        Возвращает список со списками IP-адресов

        :return:
            Возвращает список словарей со всеми списками IP-адресов (ip_address_lists)
        """
        url = 'https://192.168.56.10:8433/aliases/ip_address_lists'
        return self.get_from_endpoint(url)

    def get_auth_sessions(self):
        """
        Возвращает список авторизованных пользователей

        :return:
            Возвращает список словарей с информацией об авторизованных сессиях пользователей
        """
        url = 'https://192.168.56.10:8433/monitor_backend/auth_sessions'
        return self.get_from_endpoint(url)


    def block_user(self, username):
        """
        Блокирует пользователя по логину, путём добалвения в правило для блокировки

        :parameters:
            username
                логин пользователя
        """
        if self.check_status_user(username):
            print(f'Пользователь {username} уже заблокирован')
            return
        else:
            block_rule = self.find_rule_for_block()
            user_id = self.find_user_by_name(username)
            block_rule['source_addresses'].append(f"user.id.{user_id}")
            url = f'https://192.168.56.10:8433/firewall/rules/forward/{block_rule.pop("id")}'
            data = block_rule
            response = self.put_to_endpoint(url, data)
            if response is not None:
                print(f'Пользователь {username} заблокирован')
            else:
                print(f'Не удалось заблокировать пользователя {username}')

    def unblock_user(self, username):
        """
        Разблокирует пользователя по логину, путём удаления из правила для блокировки

        :parameters:
            username
                логин пользователя
        """
        if not self.check_status_user(username):
            print(f'Пользователь {username} не блокируется')
            return
        else:
            block_rule = self.find_rule_for_block()
            user_id = self.find_user_by_name(username)
            block_rule['source_addresses'].remove(f"user.id.{user_id}")
            url = f'https://192.168.56.10:8433/firewall/rules/forward/{block_rule.pop("id")}'
            data = block_rule
            response = self.put_to_endpoint(url, data)
            if response is not None:
                print(f'Пользователь {username} разблокирован')
            else:
                print(f'Не удалось разблокировать пользователя {username}')

    def block_ip(self, address):
        """
        Блокирует IP-адрес, путём добавления в список для блокировки IP-адресов

        :parameters:
            address
                IP-адрес
        """

        if self.check_status_ip(address):
            print(f'Адрес {address} уже заблокирован')
            return
        else:
            blocklist_id, data = self.find_blocklist()
            data['values'].append(address)
            data.pop('type', None)
            url = f'https://192.168.56.10:8433/aliases/ip_address_lists/{blocklist_id}'
            response = self.put_to_endpoint(url, data)
            if response is not None:
                print(f'Адрес {address} заблокирован')
            else:
                print(f'Не удалось заблокировать адрес {address}')

    def unblock_ip(self, address):
        """
        Разблокирует IP-адрес, путём удаления из списка для блокировки IP-адресов

        :parameters:
            address
                IP-адрес
        """
        print("Разлокируется "+str(address))
        """if not self.check_status_ip(address):
            print(f'Адрес {address} не блокируется')
            return
        else:
            blocklist_id, data = self.find_blocklist()
            data['values'].remove(address)
            data.pop('type', None)
            url = f'{self.base_url}/aliases/ip_address_lists/{blocklist_id}'
            response = self.put_to_endpoint(url, data)
            if response is not None:
                print(f'Адрес {address} разблокирован')
            else:
                print(f'Не удалось разблокировать адрес {address}')"""

    def get_blocked_users(self):
        """
        Возвращает список заблокированных пользователей

        :return:
            Возвращает список с логинами заблокированных пользователей из правила для блокировки
        """
        blocked_users_list = []
        users_list = self.get_users_list()
        for blocked_user in self.find_rule_for_block()['source_addresses']:
            for user in users_list:
                if blocked_user.replace("user.id.", "") in str(user["id"]):
                    blocked_users_list.append(user["login"])
        return blocked_users_list


    def check_status_ip(self, address):
        """
        Проверяет статус блокировки IP-адреса

        :parameters:
            address
                IP-адрес для проверки

        :return:
            Возвращает "True", если IP-адрес находится в списке для блокировки, 
            "False", если IP-адреса нет в списке для блокировки
        """
        if address in self.find_blocklist()[1]['values']:
            return True
        else:
            return False

    def check_status_user(self, username):
        """
        Проверяет статус блокировки пользователя

        :parameters:
            username
                логин пользователя

        :return:
            Возвращает "True", если логин находится в правиле для блокировки, 
            "False", если логина нет в правиле для блокировки
        """
        if username in self.get_blocked_users():
            return True
        else:
            return False

    def find_rule_for_block(self):
        """
        Возвращает правило для блокировки

        :return:
            Возвращает словарь с правилом для блокировки
        """
        for rule in self.get_rules_list():
            if rule["id"] == 500:
                return(rule)
        print("Блокирующее правило не найдено")
        return self.logout()

    def find_user_by_name(self, username):
        """
        Выполняет поиск по логину среди всех пользователей и возвращает ID
        
        :parameters:
            username
                логин пользователя

        :return:
            Возвращает ID пользователя
        """
        for user in self.get_users_list():
            if user["login"] == username:
                return(user["id"])
        print("Пользователь не найден")
        return self.logout()

    def find_user_by_address(self, address):
        """
        Выполняет поиск по адресу среди авторизованных пользователей и возвращает логин

        :parameters:
            address
                серый или белый IP-адерс пользователя

        :return:
            Возвращает логин пользователя
        """
        for session in self.get_auth_sessions():
            if session["subnet"] == f'{address}/32':
                return session["login"]
            if session["external_ip"] == address:
                return session["login"]
        print(f"Пользователь с адресом {address} не найден")
        return self.logout()

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


"""
with Ideco(ip=config("IDECO_RCOD"), port='8443', user=config("IDECO_USER"), password=config("IDECO_PASS")) as api_client:
    print(api_client.unblock_user("m.ognev"))
    #print(api_client.unblock_ip(''))

"""
