from typing import Union


class IncomeTypes:
    """
    **INDIVIDUAL**: для доходов от физических лиц из РФ

    **ENTITY**: для доходов от ИП или компаний из РФ

    **FOREIGN**: для всех доходов от лиц или компаний из других стран
    """

    INDIVIDUAL = "FROM_INDIVIDUAL"
    ENTITY = "FROM_LEGAL_ENTITY"
    FOREIGN = "FROM_FOREIGN_AGENCY"


class Client:
    """
    :param data: словарь из JSON'a от ФНС
    :type data: ``dict``
    :param inn: ИНН клиента, если известен. Обязательно для ИП и юрлиц из России.
    :type inn: ``int`` or ``str``, optional
    :param display_name: название ИП, юрлица или иностранной компании, желательно указывать, чтобы ФНС не ругалась
    :type display name: ``str``
    :param income_type: тип плательщика: физлицо, российская компания или иностранная. Есть объект, чтобы указывать
    корректно (TODO: Женя, добавь ссылку)
    :type icome_type: ``str``
    """
    def __init__(
        self,
        data: dict = None,
        inn: Union[str, int] = None,
        display_name: str = None,
        income_type: str = None,
    ):
        if data is None:
            data = {}
        self.inn = str(data.get("inn", inn)) if inn else None
        self.income_type = data.get(
            "incomeType", IncomeTypes.INDIVIDUAL if not income_type else income_type
        )
        if self.inn and self.income_type == IncomeTypes.INDIVIDUAL:
            self.income_type = IncomeTypes.ENTITY
        self.contact_phone = data.get("contactPhone", None)
        self.display_name = (
            data.get("displayName", None) if not display_name else display_name
        )

    def __dict__(self):
        return {
            "incomeType": self.income_type,
            "inn": self.inn,
            "display_name": self.display_name,
            "contact_phone": self.contact_phone,
        }

    def __iter__(self):
        for k, v in self.__dict__().items():
            yield k, v
