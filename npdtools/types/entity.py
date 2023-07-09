from enum import StrEnum
from typing import Any

from pydantic import BaseModel, field_validator


class ClientType(StrEnum):
    """
    **individual**: для доходов от физических лиц из РФ

    **legal**: для доходов от ИП или компаний из РФ

    **foreign**: для всех доходов от лиц или компаний из других стран
    """

    individual = "FROM_INDIVIDUAL"
    legal = "FROM_LEGAL_ENTITY"
    foreign = "FROM_FOREIGN_AGENCY"


class PartnerInfo(BaseModel):
    code: str | None
    logo: str | None
    inn: str | None
    name: str | None


class ClientInfo(BaseModel):
    inn: str | None = None
    name: str | None = None
    type: ClientType = ClientType.individual
    phone: str | None = None
    email: str | None = None

    def fns_export(self):
        return {
            "incomeType": str(self.type.value),
            "inn": self.inn,
            "displayName": self.name,
            "contactPhone": self.phone,
        }


class EmployeeInfo(BaseModel):
    inn: str | None
    profession: str | None
    description: list[dict[str, Any]] | None
    email: str | None
    phone: str | None

    @field_validator("profession", mode="before")
    @classmethod
    def profession_normalization(cls, value: str | None):
        if value is None or value == "":
            return None

        return value


class BankAccount(BaseModel):
    name: str
    bik: str | None
    account: str | None
    corr: str | None


class BankPhone(BaseModel):
    name: str
    id: int | None = None
    phone: str


class AcquiringInfo(BaseModel):
    merchant_id: Any
    acquirer_id: Any
    acquirer_name: Any
    payment_url: Any
