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
		self.approved_receipt_uuid: str = data.get('approvedReceiptUuid', None)
		self.id = self.approved_receipt_uuid
		self.name: str = data.get('name', None)
		self.operation_time_str: str = data.get('operationTime', None)
		if self.operation_time_str:
			self.operation_time: datetime = datetime.strptime(self.operation_time_str, '%Y-%m-%dT%H:%M:%S%z')
		self.request_time_str: str = data.get('requestTime', None)
		if self.request_time_str:
			self.request_time: datetime = datetime.strptime(self.request_time_str, '%Y-%m-%dT%H:%M:%S%z')
		self.payment_type: str = data.get('paymentType', None)
		self.partner_code: str = data.get('partnerCode', None)
		self.total_amount: Union[int, float] = data.get('totalAmount', None)
		self.source_device_id: str = data.get('sourceDeviceId', None)
		self.device_id: str = self.source_device_id
		self.ignore_max_total_income_restriction = data.get('ignoreMaxTotalIncomeRestriction', None)

		# Описание клиента
		self.client: dict = data.get('client', None)
		if self.client:
			self.client = Client(self.client)

		# Отмена платежа
		self.cancellation_info = None
		if "cancellationInfo" in data:
			self.cancellation_info: CancellationInfo = CancellationInfo(data["cancellationInfo"])
		self.raw = data

	def __repr__(self):
		is_cancel = "Cancel income" if self.cancellation_info else "Income"
		return f"<{is_cancel} #{self.id} ({self.total_amount} rub.) at {self.operation_time_str}>"

	def __str__(self):
		return self.__repr__()


