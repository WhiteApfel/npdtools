from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable, Literal

from pydantic import BaseModel, Field, model_validator

from npdtools.types.entity import (
    AcquiringInfo,
    BankAccount,
    BankPhone,
    ClientInfo,
    ClientType,
    EmployeeInfo,
)
from npdtools.types.income import PaymentTypes
from npdtools.types.service import Service


class PaymentOption(BaseModel):
    """
    Объект со способом приёма денег по счёту

    Attributes:
        id: Идентификатор способа оплаты
        type: Тип: по телефону или по номер счёта
        bank: Собственно, сами сведения о способе приёма
        is_favorite: Является ли способ приоритетным. Может быть один на каждый ``PaymentOption.type``
        is_for_pa: Хз, зачем и что такое
        raw: JSON'подобный словарь, содержащий необработанный ответ ФНС
    """

    id: int
    type: Literal["ACCOUNT", "PHONE"]
    bank: BankAccount | BankPhone
    is_favorite: bool = Field(..., alias="favorite")
    is_for_pa: bool = Field(..., alias="availableForPa")  # Хз, зачем это
    raw: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["raw"] = values.copy()
        bank = {}

        if values.get("type") == "PHONE":
            bank = BankPhone(
                id=values.get("bankId"),
                name=values.get("bankName"),
                phone=values.get("phone"),
            )
        elif values.get("type") == "ACCOUNT":
            bank = BankAccount(
                name=values.get("bankName"),
                bik=values.get("bankBik"),
                account=values.get("currentAccount"),
                corr=values.get("corrAccount"),
            )

        values["bank"] = bank

        return values


class PaymentOptions(BaseModel):
    """
    Итерируемый список способов получения денег по счёту

    Attributes:
        options: Сам список хранится в этой переменной, но работать можно и с самим объектом сразу
    """

    options: list[PaymentOption] = Field(..., alias="items")

    def __iter__(self):
        return iter(self.options)

    def __getitem__(self, item) -> PaymentOption:
        return self.options[item]

    def __len__(self) -> int:
        return len(self.options)


class ReceiptTemplate(BaseModel):
    """
    Настройки чека

    Notes: Редактор чека
        Отображение всех полей настраивается в [редакторе чека](https://lknpd.nalog.ru/settings/checks-editor).

        Содержимое ``profession`` и ``description`` можно отредактировать.
        Содержимое ``email`` и ``phone`` изменяется только через их смену в профиле.

        **Применяется только к вновь создаваемым счетам.**

    Attributes:
        profession: Строка, описывающая деятельность самозанятого
        description: Список дополнительного описания деятельности
        email: Адрес электронной почты
        phone: Номер телефона

    """

    profession: str | None = None
    phone: str | None = None
    email: str | None = None
    description: list[dict[str, Any]] | None = Field(None)


class Invoice(BaseModel):
    """
    Attributes:
        invoice_id: Номер счёта
        receipt_id: Номер чека, выданного к этому счёту, если, конечно, выдан
        services: Список позиций в чеке
        url: Ссылка на страницу со счётом. Можно отправить контрагенту
        status: Статус счёта
        payment_type: Способ получения денег
        total_amount: Общая сумма всех позиций в счёте
        total_tax: Сумма налогов за этот счёт
        commission: Комиссия за получение денег. Сейчас её нет или она равна нулю
        created_at: Время создания счёта
        paid_at: Время оплаты счёта
        canceled_at: Время отмены счёта
        bank: Сведения о способе получения денег по счёту
        client_info: Сведения о клиенте
        employee_info: Сведения о самозанятом
        acquiring_info: Сведения об эквайринге, если для получения используется он (TODO: Возможно, надо перенести в bank_info)
        receipt_template: Сведения о самозанятом для отображения в счёте и чеке
        type: Способ создания счёта, обычно ``MANUAL``
        auto_create_receipt: Был ли счёт создан автоматически

        uuid: Технический идентификатор счёта в ФНС
        fid: Ещё один рандомный идентификатор
    """

    invoice_id: int = Field(..., alias="invoiceId")
    uuid: str
    receipt_id: str | None = Field(..., alias="receiptId")
    fid: int

    services: list[Service]

    url: str = Field(..., alias="transitionPageURL")

    status: Literal[
        "CREATED", "CANCELLED", "PAID_WITHOUT_RECEIPT", "PAID_WITH_RECEIPT"
    ] | str

    payment_type: PaymentTypes = Field(..., alias="paymentType")

    total_amount: Decimal = Field(..., alias="totalAmount")
    total_tax: Decimal = Field(..., alias="totalTax")
    commission: Decimal | None = None

    created_at: datetime = Field(..., alias="createdAt")
    paid_at: datetime | None = Field(None, alias="paidAt")
    canceled_at: datetime | None = Field(None, alias="cancelledAt")

    bank: BankAccount | BankPhone
    client_info: ClientInfo
    employee_info: EmployeeInfo
    acquiring_info: AcquiringInfo

    receipt_template: ReceiptTemplate | None = Field(..., alias="receiptTemplate")
    type: Literal["MANUAL"]
    auto_create_receipt: bool | None = Field(None, alias="autoCreateReceipt")

    @property
    def is_paid(self) -> bool:
        """
        Returns:
            bool: Оплачен ли счёт
        """
        return self.paid_at is not None

    @property
    def is_canceled(self) -> bool:
        """
        Returns:
            bool: Отменён ли счёт
        """
        return self.canceled_at is not None

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["raw"] = values.copy()

        client_info: ClientInfo = ClientInfo(
            inn=values.get("clientInn", None),
            name=values.get("clientDisplayName", None),
            type=values.get("clientType", ClientType.individual),
            phone=values.get("clientContactPhone", None),
            email=values.get("clientEmail", None),
        )
        employee_info: EmployeeInfo = EmployeeInfo(
            inn=values.get("inn", None),
            profession=values.get("profession", None),
            description=values.get("description", None),
            email=values.get("email", None),
            phone=values.get("phone", None),
        )

        acquiring_info: AcquiringInfo = AcquiringInfo(
            merchant_id=values.get("merchantId", None),
            acquirer_id=values.get("acquirerId", None),
            acquirer_name=values.get("acquirerName", None),
            payment_url=values.get("paymentUrl", None),
        )

        bank = {}

        if values.get("paymentType") == "PHONE":
            bank = BankPhone(
                id=values.get("bankId"),
                name=values.get("bankName"),
                phone=values.get("phone"),
            )
        elif values.get("paymentType") == "ACCOUNT":
            bank = BankAccount(
                name=values.get("bankName"),
                bik=values.get("bankBik"),
                account=values.get("currentAccount"),
                corr=values.get("corrAccount"),
            )

        values["bank"] = bank
        values["employee_info"] = employee_info
        values["client_info"] = client_info
        values["acquiring_info"] = acquiring_info

        return values


class InvoicesList(BaseModel):
    """
    Содержит сведения о счетах и пагинации

    Attributes:
        invoices: Список счетов
        has_more: Есть ли ещё счета для получения
        offset: Отступ от начала
        limit: Количество в выдаче
    """

    invoices: list[Invoice] = Field(..., alias="items")
    has_more: bool = Field(..., alias="hasMore")
    offset: int = Field(..., alias="currentOffset")
    limit: int = Field(..., alias="currentLimit")

    def __iter__(self) -> Iterable[Invoice]:
        return iter(self.invoices)

    def __getitem__(self, item) -> Invoice:
        return self.invoices[item]
