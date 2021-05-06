from typing import Union
from httpx._models import Response
from datetime import datetime
from npdtools.types import Services, Client, Service


class CancellationInfo:
	def __init__(self, data: dict):
		self.operation_time_str: str = data.get('operationTime', None)
		self.operation_time = datetime.strptime(self.operation_time_str, '%Y-%m-%dT%H:%M:%S%z')
		self.comment = data.get('comment', None)
		self.raw = data


class IncomeInfo:
	"""
	Объект "чека". Он страшненький, потому что ФНС не могёт в стандарты и унификации.

	**Атрибуты**

	:param id: ID/номер чека. Например, 201cc5uzeg
	:type id: ``str``
	:param name: Название чека (обычно совпадает с названием товара/услуги)
	:type name: ``str``
	:param operation_time: Дата проведения операции
	:type operation_time: ``datetime`` or ``None``
	:param request_time: Дата обращения метода к API (хз, как ещё объяснить)
	:type request_time: ``datetime`` or ``None``
	:param total_amount: Итог. Полная стоимость чека
	:type total_amount: ``float``
	:param client: Информация о клиенте, будь то ФЛ, ИП или прочая ересь.
	:type client: Client or ``None``
	:param services: Объект с позициями чека
	:type services: Services or ``None``
	:param cancellation_info: Информация об аннулировании чека, если он аннулирован, иначе дырочка от бублика
	:type cancellation_info: CancellationInfo or ``None``
	:param raw: Чистые данные от ФНС. Можно посмотреть модельки ответов тут (TODO: сделай ссылку)
	:type raw: ``dict``

	"""
	def __init__(self, response: Union[Response, dict] = None):
		# Приведение данных к чему-то адекватному
		data: dict = response.json() if type(response) is Response else response if response else dict()
		data: dict = data if len(data) > 1 and "IncomeInfo" not in data else data["incomeInfo"]

		# Единственная адекватная часть 🎉
		self.id: str = data.get('approvedReceiptUuid', None)
		self.name: str = data.get('name', None)
		self.total_amount: Union[int, float] = data.get('totalAmount', None)

		# Игра с цифрами
		if data.get('operationTime', None):
			self.operation_time: datetime = datetime.strptime(data.get('operationTime', None), '%Y-%m-%dT%H:%M:%S%z')
		if data.get('requestTime', None):
			self.request_time: datetime = datetime.strptime(data.get('requestTime', None), '%Y-%m-%dT%H:%M:%S%z')

		# Описание клиента
		self.client: dict = data.get('client', None)
		if self.client:
			self.client = Client(self.client)
		if "clientDisplayName" in data:
			self.client = Client(display_name=data.get('clientDisplayName', None), inn=data.get('clientInn'), )

		# Списочек с покупками
		self.services = data.get("services", Services())
		if len(self.services):
			self.services = Services([Service(wa['name'], wa['amount'], wa['quantity']) for wa in self.services])

		# Отмена платежа
		self.cancellation_info = None
		if data.get("cancellationInfo", None):
			self.cancellation_info: CancellationInfo = CancellationInfo(data["cancellationInfo"])

		self.raw = data

	def __repr__(self):
		is_cancel = "Cancel income" if self.cancellation_info else "Income"
		return f"<{is_cancel} #{self.id} ({self.total_amount} rub.) at {self.operation_time.isoformat()}>"

	def __str__(self):
		return self.__repr__()


