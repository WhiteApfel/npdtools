from camel_converter import to_snake
from typing import Union
from httpx._models import Response
from datetime import datetime
from npdtools.types import Services, Client


class CancellationInfo:
	def __init__(self, data: dict):
		self.operation_time_str: str = data.get('operationTime', None)
		self.operation_time = datetime.strptime(self.operation_time_str, '%Y-%m-%dT%H:%M:%S%z')
		self.comment = data.get('comment', None)
		self.raw = data


class IncomeInfo:
	def __init__(self, response: Union[Response, dict] = None):
		data: dict = response.json() if type(response) is Response else response if response else dict()
		data: dict = data if len(data) > 1 and "IncomeInfo" not in data else data["IncomeInfo"]
		self.id = data.get('approvedReceiptUuid', None)
		self.name: str = data.get('name', None)
		if data.get('operationTime', None):
			self.operation_time: datetime = datetime.strptime(data.get('operationTime', None), '%Y-%m-%dT%H:%M:%S%z')
		if data.get('requestTime', None):
			self.request_time: datetime = datetime.strptime(data.get('requestTime', None), '%Y-%m-%dT%H:%M:%S%z')
		self.total_amount: Union[int, float] = data.get('totalAmount', None)
		self.device_id: str = data.get('sourceDeviceId', None)
		self.ignore_max_total_income_restriction = data.get('ignoreMaxTotalIncomeRestriction', None)
		self.tax_period_id: int = data.get('taxPeriodId', None)

		# Описание клиента
		self.client: dict = data.get('client', None)
		if self.client:
			self.client = Client(self.client)
		if "clientDisplayName" in data:
			self.client = Client(display_name=data.get('clientDisplayName', None), inn=data.get('clientInn'), )

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


