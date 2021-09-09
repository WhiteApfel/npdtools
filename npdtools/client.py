from httpx import Client as HttpxClient
from httpx import codes
from string import ascii_lowercase, digits
from random import choice
from time import strftime
from typing import Union
from datetime import datetime, timedelta
from re import match
from npdtools.types import Client, Services, Service, IncomeInfo
from npdtools.errors import FNSError


class NPDTools:
	"""
	Сама магическая штука для работы с чеками самозанятого

	**Аргументы**
	:param login: Логин, но на самом деле ваш ИНН, за исключением редких случаев
	:type login: ``str``
	:param password: Пароль от личного кабинета.
	Если авторизация через Госуслуги, то читать заметку (TODO: добавить ссылку)
	:type password: ``str``
	:param api_url: На случай смены адреса апишки
	:type api_url: ``str``, optional
	"""
	def __init__(self, login: str, password: str, api_url: str = None):
		self.__login = login
		self.__password = password

		self.__api = 'https://lknpd.nalog.ru/api/v1' if not api_url else api_url
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
		else:
			raise FNSError(response)
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
			self.inn = r_data['profile']['inn']
			self.__token = r_data['token']
			self.__token_lifetime = r_data['tokenExpireIn']
			self.__refresh_token = r_data['refreshToken']
		else:
			raise FNSError(response)

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
		r = r'([0-9]{4})\-([0-1][0-9])\-([0-3][0-9])T([0-2][0-9])\:([0-5][0-9])\:([0-5][0-9])(\.[0-9]+)?' \
			r'([\+\-])([0-1][0-9]):([013][05])'
		return bool(match(r, date))

	def add_income(self, services: Union[Services, Service, list, tuple], client: Union[Client, list, tuple] = None, date: Union[datetime, str] = None):
		"""
		Метод выдачи чека, декларирования дохода, регистрации поступления, документирование прихода. И в одном флаконе.

		:param services: Товары и услуги в родном формате
		:type services: Services or Service
		:param client: Объект клиента, если это организация или ИП
		:type client: ``Client``, optional
		:param date: На когда регистрировать приход. По умолчанию — сейчас
		:type date: ``datetime`` or ``str``, optional
		:return: Объект чека, согласно модельке
		:rtype: IncomeInfo
		"""
		if (date and type(date) is str) and not self.datestr_valid(date):
			raise ValueError("_date_ must be like '2021-05-04T19:31:46+03:00'")
		elif date and type(date) is datetime and date < datetime.now():
			date = date.replace(microsecond=0).astimezone().isoformat()
		if type(services) is Service:
			services = Services(services)
		elif type(services) in [tuple, list] \
				and len(services) == 3 \
				and type(services[0]) is str and type(services[1]) in [int, float] and type(services[2]) is int:
			services = Services(services)
		total_amount = services.total_amount
		if type(client) in [tuple, list] and len(client) in [1, 2]:
			if len(client) == 1:
				client = [client[0], None]
			client = Client(display_name=client[0], inn=client[1])
		data = {
			'paymentType': 'CASH',
			'ignoreMaxTotalIncomeRestriction': False,
			'client': dict(client),
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

	def cancel_income(self, id: str, comment: str = 'Чек сформирован ошибочно', date: Union[datetime, str] = None):
		"""
		Отменяем всё то, что тут наделали

		:param id: ID/номер чека
		:type id: ``str``
		:param comment: Комментарий для отмены. По умолчанию ``Чек сформирован ошибочно``
		:type comment: ``str``, optional
		:param date: Время возврата, например, если вчера произошёл возврат денег, то желательно указать эту дату.
		По умолчанию будет выставлено "сейчас"
		:type date: ``datetime`` or ``str``, optional
		:return: Объект чека, согласно модельке
		:rtype: IncomeInfo
		"""
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
			return IncomeInfo(response.json())
		else:
			print(response.status_code)
			print(response.text)
			print(response.headers)
			print(data)
			raise ValueError("Здесь нужна ошибка ответа")

	def incomes(self, start: Union[str, datetime] = None, end:  Union[str, datetime] = None, period: timedelta = None,
				sort_type='operation_time', desc=True, limit=10):
		"""
		Списочек операций с фильтрами

		:param start: с какого числа ищем чеки
		:type start: ``datetime`` or ``str``, optional
		:param end: до какого числа ищем чеки
		:type end:  ``datetime`` or ``str``, optional
		:param period: Если не указаны первые два параметра, от текущего момента возмутся 30 дней
		:type period:  ``timedelta``, optional
		:param sort_type: по какому параметру сортироват, по умолчанию — по времени операции
		:type sort_type: ``str``, optional
		:param desc: по убыванию? По умолчанию — да.
		:type desc: ``bool``, optional
		:param limit: сколько максимум чеков отобразить (но не больше тысячи)
		:type limit: ``int``
		:return: список счетов
		:rtype: List[IncomeInfo]
		"""
		if not start or not end:
			end = datetime.now().replace(microsecond=0).astimezone().isoformat()
			delta = period if period else timedelta(days=30)
			start = (datetime.now() - delta).replace(microsecond=0).astimezone().isoformat()
		elif (start and ((type(start) is str and self.datestr_valid(start)) or type(start) is datetime)) and \
			(end and ((type(end) is str and self.datestr_valid(end)) or type(end) is datetime)):
			if type(start) is datetime:
				start = start.replace(microsecond=0).astimezone().isoformat()
			if type(start) is datetime:
				end = end.replace(microsecond=0).astimezone().isoformat()
		else:
			raise ValueError("Что-то не так с датами. Но это не точно.")
		params = {
			'from': start,
			'to': end,
			'offset': 0,
			'sortBy': f'{sort_type}:{"desc" if desc else "asc"}',
			'limit': limit
		}
		response = self.client.get(f"{self.__api}/incomes", params=params, headers=self.__headers())
		if response.status_code == codes.OK and "json" in response.headers["content-type"]:
			r_data = response.json()

			return [IncomeInfo(c) for c in r_data['content']]
