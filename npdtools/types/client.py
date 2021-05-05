class IncomeTypes:
	FROM_INDIVIDUAL = "FROM_INDIVIDUAL"
	FROM_LEGAL_ENTITY = "FROM_LEGAL_ENTITY"
	FROM_FOREIGN_AGENCY = "FROM_FOREIGN_AGENCY"


class Client:
	def __init__(self, data: dict = None, inn: str = None, display_name: str = None):
		if data is None:
			data = {}
		self.inn = data.get('inn', None) or inn
		self.income_type = data.get('incomeType', IncomeTypes.FROM_INDIVIDUAL)
		if self.inn and self.income_type == IncomeTypes.FROM_INDIVIDUAL:
			self.income_type = IncomeTypes.FROM_LEGAL_ENTITY
		self.contact_phone = data.get('contactPhone', None)
		self.display_name = data.get('displayName', None) or display_name

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
