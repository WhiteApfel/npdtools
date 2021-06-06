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
	"""
	Штучка хранит в себе позиции товаров и услуг. А ещё позволяет добавлять новые. Удалять пока-что не позволяет, так
	что будь аккуратнее, а то придётся всё делать заново. Принимает либо Service'ы через запятую, либо листы/туплы в
	формате [название, цена, количество], например, ["Отсосал на трассе и принял на лицо", 5600, 1], через ту же запятую.
	Либо ничего не принимает. Да, она такая, неприхотливая.

	**Аргументы**

	:param ``*args``: можно вставить какое-нибудь количество экземпляров позиций
	:type ``*args``: Service

	**Атрибуты**

	:param total_amount: Итоговая стоимость всех позиций с округлением до копеек
	:type total_amount: ``float``
	"""
	def __init__(self, *args):
		self.services: list[Service] = []
		if all([type(a) is Service for a in args]):
			self.services: List[Service] = list(args)
		elif all([type(a[0]) is str and type(a[1]) in [int, float] and type(a[2]) is int for a in args]):
			self.services: List[Service] = [Service(a[0], a[1], a[2]) for a in args]

	def add(self, name: str, amount: Union[int, float], quantity: int = 1):
		"""
		Используется для добавления позиции. Вдруг понадобится.

		:param name: Название позиции. Например, ``Минет в машине на Фрунзе`` или ``Анальная пробка ручной работы``
		:type name: ``str``
		:param amount: Цена позиции (за единицу, т.к. можно указать количество)
		:type amount: ``int`` or ``float``
		:param quantity: Количество товара/услуг этой позиции. Только целочисленное
		:type quantity: ``int``, optional, default ``1``
		"""
		self.services.append(Service(name, amount, quantity))

	@property
	def total_amount(self) -> float:
		return round(float(sum([s.amount * s.quantity for s in self.services])), 2)

	def __iter__(self):
		for service in self.services:
			yield dict(service)

	def __len__(self):
		return len(self.services)
