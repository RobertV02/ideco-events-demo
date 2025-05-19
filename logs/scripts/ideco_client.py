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

	def logout(self):
		"""
		Выполняет разавторизацию, меняет статус авторизации "self.logged"
		
		"""
		if self.logged:
				url = f'{self.base_url}/web/auth/login'
				response = self.session.delete(url)
				if response.status_code == 200:
						self.logged = False
						print("Выход выполнен")
				response.raise_for_status()
	
	def login(self):
					"""
					Выполняет авторизацию, меняет статус авторизации "self.logged"

					"""
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
			
	def get_ip_address_lists(self):
			url = f'{self.base_url}/aliases/ip_address_lists'
			return self.get_from_endpoint(url)

	def find_blocklist(self):
			"""
			Возвращает список для блокировки IP-адресов

			:return:
					Возвращает словарь со списком для блокировки по IP-адресу
			"""
			for list in self.get_ip_address_lists().items():
					if list[1]["title"] == 'ip для блокировки':
							return list
			print("Список для блокировки не найден")
			return self.logout()

	def put_to_endpoint(self, url: str, data: dict):
			"""Универсальный PUT → возвращает JSON или бросает ошибку."""
			r = self.session.put(url, json=data, timeout=10)
			r.raise_for_status()
			return r.json()
			
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
					url = f'{self.base_url}/aliases/ip_address_lists/{blocklist_id}'
					response = self.put_to_endpoint(url, data)
					if response is not None:
							print(f'Адрес {address} заблокирован')
					else:
							print(f'Не удалось заблокировать адрес {address}')
	
	
