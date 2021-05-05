from httpx import Client as HttpxClient
from httpx import codes
from string import ascii_lowercase, digits
from random import choice
from time import strftime
from typing import Union
from datetime import datetime
from re import match
from npdtools.types import Client, Services, Service, IncomeInfo


class NPDTools:
	def __init__(self, login: str, password: str, endpoint: str = None):
		self.__login = login
		self.__password = password

		self.__api = 'https://lknpd.nalog.ru/api/v1' if not endpoint else endpoint
		self.__client = None

		self.__token = None
		self.__token_lifetime = None
		self.__refresh_token = None
		self.__device_id = None
		self.inn = None

		self.__user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'

	@property
	def client(self):
		if not self.__client:
			self.__client = HttpxClient()
			if not self.__refresh_token:
				self.__auth()
		return self.__client

	@property
	def device_id(self):
		if not self.__device_id:
			self.__device_id = "".join([choice(ascii_lowercase + digits) for _ in range(21)])
		return self.__device_id

	@property
	def token(self):
		if self.__token and self.__token_lifetime and self.__token_lifetime > strftime("%Y-%m-%dT%H:%M:%SZ"):
			return self.__token
		elif not self.__refresh_token:
			self.__auth()
		data = {
			'deviceInfo': {
				'appVersion': '1.0.0',
				'sourceDeviceId': self.device_id,
				'sourceType': 'WEB',
				'metaDetails': {
					'userAgent': self.__user_agent
				}
			},
			'refreshToken': self.__refresh_token
		}
		response = self.client.post(f"{self.__api}/auth/token", json=data, headers=self.__headers('sales', False))
		if response.status_code == codes.OK and "json" in response.headers["content-type"]:
			r_data = response.json()
			if "refreshToken" in r_data and r_data['refreshToken']:
				self.__refresh_token = r_data['refreshToken']
			self.__token = r_data["token"]
			self.__token_lifetime = r_data['tokenExpireIn']
		return self.__token

	def __auth(self):
		data = {
			'username': self.__login,
			'password': self.__password,
			'deviceInfo': {
				'sourceDeviceId': self.device_id,
				'sourceType': 'WEB',
				'appVersion': '1.0.0',
				'metaDetails': {
					'userAgent': self.__user_agent
				}
			}
		}
		response = self.client.post(f"{self.__api}/auth/lkfl", headers=self.__headers(token=False), json=data)
		if response.status_code == codes.OK and "json" in response.headers["content-type"]:
			r_data = response.json()
			self.INN = r_data['profile']['inn']
			self.__token = r_data['token']
			self.__token_lifetime = r_data['tokenExpireIn']
			self.__refresh_token = r_data['refreshToken']

	def __headers(self, referer: str = None, token: bool = True):
		headers = {
			'accept': 'application/json, text/plain, */*',
			'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
			'cache-control': 'no-cache',
			'content-type': 'application/json',
			'pragma': 'no-cache',
			'referer': f'https://lknpd.nalog.ru/{referer if referer else ""}',
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
			'sec-gpc': '1'
		}
		if token:
			headers['authorization'] = f'Bearer {self.token}'
		return headers

	def datestr_valid(self, date: str):
		r = r'([0-9]{4})\-([0-1][0-9])\-([0-3][0-9])T([0-2][0-9])\:([0-5][0-9])\:([0-5][0-9])([\+\-])([0-1][0-9]):([013][05])'
		return bool(match(r, date))

	def add_income(self, services: Union[Services, Service], inn: str = None, date: Union[datetime, str] = None):
		if (date and type(date) is str) and not self.datestr_valid(date):
			raise ValueError("_date_ must be like '2021-05-04T19:31:46+03:00'")
		if type(services) is Service:
			services = Services(services)
		total_amount = services.total_amount
		data = {
			'paymentType': 'CASH',
			'ignoreMaxTotalIncomeRestriction': False,
			'client': dict(Client(inn=inn)),
			'requestTime': datetime.now().replace(microsecond=0).astimezone().isoformat(),
			'operationTime': datetime.now().replace(microsecond=0).astimezone().isoformat() if not date else date,
			'services': list([dict(s) for s in services]),
			'totalAmount': round(float(total_amount), 2)
		}
		response = self.client.post(f"{self.__api}/income", json=data, headers=self.__headers())
		if response.status_code == codes.OK and "json" in response.headers["content-type"]:
			r_data = response.json()
			return IncomeInfo({**data, **r_data})
		else:
			print(response.status_code)
			print(response.text)
			print(response.headers)
			print(data)
			raise ValueError("Здесь нужна ошибка ответа")

	def cancel_income(self, id: str, comment: str = 'Чек сформирован ошибочно',date: Union[datetime, str] = None):
		if (date and type(date) is str) and not self.datestr_valid(date):
			raise ValueError("_date_ must be like '2021-05-04T19:31:46+03:00'")
		data = {
			'comment': comment,
			'requestTime': datetime.now().replace(microsecond=0).astimezone().isoformat(),
			'operationTime': datetime.now().replace(microsecond=0).astimezone().isoformat() if not date else date,
			'receiptUuid': id
		}
		response = self.client.post(f"{self.__api}/cancel", json=data, headers=self.__headers())
		if response.status_code == codes.OK and "json" in response.headers["content-type"]:
			r_data = response.json()
			return IncomeInfo({**r_data}['incomeInfo'])
		else:
			print(response.status_code)
			print(response.text)
			print(response.headers)
			print(data)
			raise ValueError("Здесь нужна ошибка ответа")
