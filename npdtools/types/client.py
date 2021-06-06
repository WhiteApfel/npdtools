from typing import Union

class IncomeTypes:
	INDIVIDUAL = "FROM_INDIVIDUAL"
	ENTITY = "FROM_LEGAL_ENTITY"
	FOREIGN = "FROM_FOREIGN_AGENCY"


class Client:
	def __init__(self, data: dict = None, inn: Union[str, int] = None, display_name: str = None, income_type: str = None):
		if data is None:
			data = {}
		self.inn = str(data.get('inn', None)) if not inn else str(inn)
		self.income_type = data.get('incomeType', IncomeTypes.INDIVIDUAL if not income_type else income_type)
		if self.inn and self.income_type == IncomeTypes.INDIVIDUAL:
			self.income_type = IncomeTypes.ENTITY
		self.contact_phone = data.get('contactPhone', None)
		self.display_name = data.get('displayName', None) if not display_name else display_name

	def __dict__(self):
		return {
			'incomeType': self.income_type,
			'inn': self.inn,
			'display_name': self.display_name,
			"contact_phone": self.contact_phone
		}

	def __iter__(self):
		for k, v in self.__dict__().items():
			yield k, v
