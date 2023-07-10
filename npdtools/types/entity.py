from enum import StrEnum
from typing import Any

from pydantic import BaseModel, field_validator


class ClientType(StrEnum):
    """
    Список типов клиентов

    Attributes:
        individual: Для доходов от физических лиц из РФ
        legal: Для доходов от лиц или компаний из других стран
        foreign: Для доходов от ИП или компаний из РФ
    """

    individual: str = "FROM_INDIVIDUAL"
    legal: str = "FROM_LEGAL_ENTITY"
    foreign: str = "FROM_FOREIGN_AGENCY"


class PartnerInfo(BaseModel):
    """
    Сведения о партнёре

    Attributes:
        code: Код партнёра, обычно uuid
        logo: base64 png-логотип
        inn: ИНН партнёра
        name: Краткое (красивое) название партнёра
    """

    code: str | None = None
    logo: str | None = None
    inn: str | None = None
    name: str | None = None


class ClientInfo(BaseModel):
    """
    Сведения о клиенте

    Attributes:
        inn: ИНН клиента. Для физлиц и иностранных компаний по желанию. Для российских обязательно
        name: ФИО или название компании сокращённо (например, ``ИП`` вместо ``Индивидуальный предприниматель``)
        type: Тип клиента из ClientType
        phone: Контактный номер по желанию
        email: Контактный email по желанию. Туда может приходить чек. Но не всегда
    """

    inn: str | None = None
    name: str | None = None
    type: ClientType = ClientType.individual
    phone: str | None = None
    email: str | None = None

    def fns_export(self) -> dict[str, Any]:
        """
        Экспортирует модель в json'подобный словарь

        Returns:
            Словарь в нужном ФНС формате
        """
        return {
            "incomeType": str(self.type.value),
            "inn": self.inn,
            "displayName": self.name,
            "contactPhone": self.phone,
        }


class EmployeeInfo(BaseModel):
    """
    Сведения о самозанятом

    Notes: Редактор чека
        Отображение всех полей, кроме ``inn``, настраивается в [редакторе чека](https://lknpd.nalog.ru/settings/checks-editor).

        Содержимое ``profession`` и ``description`` можно отредактировать.
        Содержимое ``email`` и ``phone`` изменяется только через их смену в профиле.

        **Применяется только к вновь создаваемым чекам.**

    Attributes:
        inn: ИНН самозанятого
        profession: Строка, описывающая деятельность самозанятого
        description: Список дополнительного описания деятельности
        email: Адрес электронной почты
        phone: Номер телефона
    """

    inn: str
    profession: str | None = None
    description: list[dict[str, Any]] | None = None
    email: str | None = None
    phone: str | None = None

    @field_validator("profession", mode="before")
    @classmethod
    def profession_normalization(cls, value: str | None):
        if value is None or value == "":
            return None

        return value


class BankAccount(BaseModel):
    name: str
    bik: str
    account: str
    corr: str


class BankPhone(BaseModel):
    name: str
    id: int | None = None
    phone: str


class AcquiringInfo(BaseModel):
    merchant_id: Any = None
    acquirer_id: Any = None
    acquirer_name: Any = None
    payment_url: Any = None
