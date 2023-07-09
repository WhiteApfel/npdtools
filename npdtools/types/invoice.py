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
    options: list[PaymentOption] = Field(..., alias="items")

    def __iter__(self):
        return iter(self.options)

    def __getitem__(self, item) -> PaymentOption:
        return self.options[item]

    def __len__(self) -> int:
        return len(self.options)


class ReceiptTemplate(BaseModel):
    profession: str | None = None
    phone: str | None = None
    email: str | None = None
    description: list[dict[str, Any]] | None = Field(None)


class Invoice(BaseModel):
    invoice_id: int = Field(..., alias="invoiceId")
    uuid: str
    receipt_id: str | None = Field(..., alias="receiptId")
    fid: int

    services: list[Service]

    url: str = Field(..., alias="transitionPageURL")

    status: Literal[
        "CREATED", "PAID_WITHOUT_RECEIPT", "PAID_WITHOUT_RECEIPT", "PAID_WITH_RECEIPT"
    ] | str

    payment_type: PaymentTypes = Field(..., alias="paymentType")

    total_amount: Decimal = Field(..., alias="totalAmount")
    total_tax: Decimal = Field(..., alias="totalTax")
    commission: Decimal | None = None

    created_at: datetime = Field(..., alias="createdAt")
    paid_at: datetime | None = Field(None, alias="paidAt")
    cancelled_at: datetime | None = Field(None, alias="cancelledAt")

    bank: BankAccount | BankPhone
    client_info: ClientInfo
    employee_info: EmployeeInfo

    receipt_template: ReceiptTemplate | None = Field(..., alias="receiptTemplate")
    type: Literal["MANUAL"]
    auto_create_receipt: bool | None = Field(None, alias="autoCreateReceipt")

    @property
    def is_paid(self) -> bool:
        return self.paid_at is not None

    @property
    def is_cancelled(self) -> bool:
        return self.cancelled_at is not None

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
    invoices: list[Invoice] = Field(..., alias="items")
    has_more: bool = Field(..., alias="hasMore")
    offset: int = Field(..., alias="currentOffset")
    limit: int = Field(..., alias="currentLimit")

    def __iter__(self) -> Iterable[Invoice]:
        return iter(self.invoices)

    def __getitem__(self, item) -> Invoice:
        return self.invoices[item]
