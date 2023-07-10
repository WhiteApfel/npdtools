import enum
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable

from pydantic import BaseModel, Field, field_validator, model_validator

from npdtools.helpers import amount_to_decimal
from npdtools.settings import LKNPD_API_V1
from npdtools.types.entity import ClientInfo, ClientType, EmployeeInfo, PartnerInfo
from npdtools.types.service import Service


class PaymentTypes(enum.StrEnum):
    """
    Attributes:
        cash: Наличными
        phone: По номеру телефона
        account: По реквизитам счёта
    """

    cash: str = "CASH"
    phone: str = "PHONE"
    account: str = "ACCOUNT"


class SortTypes(enum.StrEnum):
    """
    Attributes:
        time: Сортировка по времени
        amount: Сортировка по полной стоимости
    """

    time: str = "operation_time"
    amount: str = "total_amount"


class NewIncome(BaseModel):
    """
    Attributes:
        receipt_id: Номер чека
    """

    receipt_id: str = Field(..., alias="approvedReceiptUuid")


class CancellationInfo(BaseModel):
    """
    Сведения об аннулировании дохода

    Attributes:
        canceled_at: Время фактического возврата денег
        registered_at: Время регистрации аннулирования
        comment: Комментарий к аннулированию
        tax_period: Налоговый период в формате ``YYYYMM``
        raw: JSON'подобный словарь, содержащий необработанный ответ ФНС
    """

    canceled_at: datetime = Field(..., alias="operationTime")
    registered_at: datetime = Field(..., alias="registerTime")
    comment: str | None = None
    tax_period: int | None = Field(None, alias="taxPeriodId")
    raw: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["raw"] = values.copy()

        return values


class CanceledIncome(BaseModel):
    """
    Сведения об аннулированном чеке

    Attributes:
        receipt_id: Номер чека
        name: Название чека
        created_at: Время фактической декларации дохода
        received_at: Время получения денег
        payment_type: Вид получения денег. Всегда ``CASH``. Хз, когда не ``CASH``
        partner_code: Код партнёра, если это он регистрировал чек
        total_amount: Общая сумма дохода, за все позиции
        cancellation_info: Сведения об аннулировании
        device_id: Идентификатор устройства, с которого был зарегистрирован чек

    """

    receipt_id: str = Field(..., alias="approvedReceiptUuid")
    name: str
    created_at: datetime = Field(..., alias="requestTime")
    received_at: datetime = Field(..., alias="operationTime")
    payment_type: PaymentTypes = Field(..., alias="paymentType")
    partner_code: Any | None = Field(None, alias="partnerCode")
    total_amount: Decimal = Field(..., alias="totalAmount")
    cancellation_info: CancellationInfo = Field(..., alias="cancellationInfo")
    device_id: str | None = Field(None, alias="sourceDeviceId")

    @property
    def is_cancelled(self) -> bool:
        """
        Returns:
            bool: Является ли чек отменённым? Ну типа да, всегда, но не всегда
        """
        return self.cancellation_info is not None

    @field_validator("total_amount", mode="before")
    @classmethod
    def amount_normalizer(cls, value) -> Decimal:
        return amount_to_decimal(value)


class IncomeInfo(BaseModel):
    """
    Сведения о задекларированном доходе.

    Attributes:
        receipt_id: Номер чека
        total_amount: Общая сумма дохода, за все позиции
        services: Список позиций в чеке
        name: Название чека
        tax_period: Налоговый период в формате ``YYYYMM``
        cancellation_info: Сведения об аннулировании
        payment_type: Вид получения денег. Всегда ``CASH``. Хз, когда не ``CASH``
        created_at: Время фактической декларации дохода
        received_at: Время получения денег
        device_id: Идентификатор устройства, с которого был зарегистрирован чек
        partner_info: Сведения о партнёре
        client_info: Сведения о клиенте
        employee_info: Сведения о самозанятом
        invoice_id: Номер связанного с доходом счёта
        raw: JSON'подобный словарь, содержащий необработанный ответ ФНС
    """

    receipt_id: str = Field(..., alias="approvedReceiptUuid")
    total_amount: Decimal = Field(..., alias="totalAmount")
    services: list[Service]

    name: str
    tax_period: int | None = Field(None, alias="taxPeriodId")
    cancellation_info: CancellationInfo | None = Field(None, alias="cancellationInfo")
    payment_type: PaymentTypes = Field(..., alias="paymentType")

    created_at: datetime = Field(..., alias="requestTime")
    registered_at: datetime = Field(..., alias="registerTime")
    received_at: datetime = Field(..., alias="operationTime")

    device_id: str | None = Field(None, alias="sourceDeviceId")

    partner_info: PartnerInfo | None = None
    client_info: ClientInfo
    employee_info: EmployeeInfo

    invoice_id: int | None = Field(None, alias="invoiceId")

    raw: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def model_normalize(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["raw"] = values.copy()

        partner_info: PartnerInfo = PartnerInfo(
            code=values.get("partnerCode", None),
            logo=values.get("partnerLogo", None),
            inn=values.get("partnerInn", None),
            name=values.get("partnerDisplayName", None),
        )

        if partner_info.inn is None:
            partner_info: None = None

        client_info: ClientInfo = ClientInfo(
            inn=values.get("clientInn", None),
            name=values.get("clientDisplayName", None),
            type=values.get("incomeType", ClientType.individual),
            phone=values.get("clientContactPhone", None),
        )
        employee_info: EmployeeInfo = EmployeeInfo(
            inn=values.get("inn", None),
            profession=values.get("profession", None),
            description=values.get("description", None),
            email=values.get("email", None),
            phone=values.get("phone", None),
        )

        values["employee_info"] = employee_info
        values["client_info"] = client_info
        values["partner_info"] = partner_info

        return values

    @property
    def receipt_url(self) -> str:
        """
        Returns:
            str: Ссылка на картинку чека
        """
        return (
            f"{LKNPD_API_V1}/receipt/{self.employee_info.inn}/{self.receipt_id}/print"
        )

    @property
    def receipt_url_json(self) -> str:
        """

        Returns:
            str: Ссылка на JSON со сведениями о чеке
        """
        return f"{LKNPD_API_V1}/receipt/{self.employee_info.inn}/{self.receipt_id}/json"


class IncomesList(BaseModel):
    """
    Содержит сведения о чеках и пагинации

    Attributes:
        incomes: Список чеков
        has_more: Есть ли ещё счета для получения
        offset: Отступ от начала
        limit: Количество в выдаче
    """

    incomes: list[IncomeInfo] = Field(..., alias="content")
    has_more: bool = Field(..., alias="hasMore")
    offset: int = Field(..., alias="currentOffset")
    limit: int = Field(..., alias="currentLimit")

    def __iter__(self) -> Iterable[IncomeInfo]:
        return iter(self.incomes)

    def __getitem__(self, item) -> IncomeInfo:
        return self.incomes[item]
