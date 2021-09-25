from typing import Union, List


class Service:
    """
    Класс для комфортного создания одной позиции чека. Будь то товар, услуга или ещё непонятно что =-)

    :param name: Название позиции. Например, ``Минет в машине на Фрунзе`` или ``Анальная пробка ручной работы``
    :type name: ``str``
    :param amount: Цена позиции (за единицу, т.к. можно указать количество)
    :type amount: ``int`` or ``float``
    :param quantity: Количество товара/услуг этой позиции. Только целочисленное
    :type quantity: ``int``, optional, default ``1``
    """

    def __init__(self, name: str, amount: Union[int, float], quantity: int = 1):
        self.name: str = name
        self.amount: float = round(float(amount), 2)
        self.quantity: int = quantity

    @property
    def service_amount(self) -> float:
        return round(float(self.amount * self.quantity), 2)

    def __dict__(self):
        return {"name": self.name, "amount": self.amount, "quantity": self.quantity}

    def __iter__(self):
        for k, v in self.__dict__().items():
            yield k, v

    def __add__(self, other):
        new_services = Services()
        if type(other) is Service:
            new_services.append(other)
        elif type(other) is Services:
            new_services = other
            new_services.append(self)
        elif (
                type(other) in [tuple, list]
                and len(other) == 3
                and type(other[0]) is str
                and type(other[1]) in [int, float]
                and type(other[2]) is int
        ):
            new_services.add(other[0], other[1], other[2])
        return new_services


class Services:
    """
    Штучка хранит в себе позиции товаров и услуг. А ещё позволяет добавлять новые. Удалять пока-что не позволяет, так
    что будь аккуратнее, а то придётся всё делать заново. Принимает либо Service'ы через запятую, либо листы/туплы в
    формате ``[название, цена, количество]``, например, ``["Отсосал на трассе и принял на лицо", 5600, 1]``,
    через ту же запятую. Либо ничего не принимает. Да, она такая, неприхотливая.

    **Аргументы**

    :param ``*args``: можно вставить какое-нибудь количество экземпляров позиций
    :type ``*args``: Service

    **Атрибуты**

    :param total_amount: Итоговая стоимость всех позиций с округлением до копеек
    :type total_amount: ``float``
    """

    def __init__(self, *args: Union[Service, list, tuple[str, Union[int, float], int]]):
        self.services: list[Service] = []
        if all([type(a) is Service for a in args]):
            self.services: List[Service] = list(args)
        elif all(
                [
                    type(a[0]) is str and type(a[1]) in [int, float] and type(a[2]) is int
                    for a in args
                ]
        ):
            self.services: List[Service] = [Service(a[0], a[1], a[2]) for a in args]

    def add(self, name: str, amount: Union[int, float], quantity: int = 1):
        """
        Используется для добавления позиции напрямую по параметрам. Вдруг понадобится.

        :param name: Название позиции. Например, ``Минет в машине на Фрунзе`` или ``Анальная пробка ручной работы``
        :type name: ``str``
        :param amount: Цена позиции (за единицу, т.к. можно указать количество)
        :type amount: ``int`` or ``float``
        :param quantity: Количество товара/услуг этой позиции. Только целочисленное
        :type quantity: ``int``, optional, default ``1``
        """
        self.services.append(Service(name, amount, quantity))

    def append(self, service):
        """
        Добавляет позицию, только если она уже является экземпляром класса Service (TODO: добавь ссылку)

        :param name: Название позиции. Например, ``Минет в машине на Фрунзе`` или ``Анальная пробка ручной работы``
        :type name: ``str``
        :param amount: Цена позиции (за единицу, т.к. можно указать количество)
        :type amount: ``int`` or ``float``
        :param quantity: Количество товара/услуг этой позиции. Только целочисленное
        :type quantity: ``int``, optional, default ``1``
        """
        if type(service) is Service:
            self.services.append(service)
        else:
            raise ValueError('service must be instance of Service')

    @property
    def total_amount(self) -> float:
        return round(float(sum([s.amount * s.quantity for s in self.services])), 2)

    def __iter__(self):
        for service in self.services:
            yield dict(service)

    def __len__(self):
        return len(self.services)

    def __add__(self, other):
        new_services = self.services
        if type(other) is Service:
            new_services.append(other)
        elif type(other) is Services:
            for service in other:
                new_services.append(service)
        elif (
                type(other) in [tuple, list]
                and len(other) == 3
                and type(other[0]) is str
                and type(other[1]) in [int, float]
                and type(other[2]) is int
        ):
            new_services.append(Service(other[0], other[1], other[2]))
        return Services(*new_services)
