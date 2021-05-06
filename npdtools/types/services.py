from typing import Union, List


class Service:
	def __init__(self, name: str, amount: Union[int, float], quantity: int = 1):
		self.name: str = name
		self.amount: float = round(float(amount), 2)
		self.quantity: int = quantity

	def __dict__(self):
		return {
			'name': self.name,
			'amount': self.amount,
			'quantity': self.quantity
		}

	def __iter__(self):
		for k, v in self.__dict__().items():
			yield k, v


class Services:
	def __init__(self, *args):
		self.services: list[Service] = []
		if all([type(a) is Service for a in args]):
			self.services: List[Service] = list(args)

	def add(self, name: str, amount: Union[int, float], quantity: int = 1):
		self.services.append(Service(name, amount, quantity))

	@property
	def total_amount(self):
		return sum([s.amount * s.quantity for s in self.services])

	def __iter__(self):
		for service in self.services:
			yield dict(service)

	def __len__(self):
		return len(self.services)
