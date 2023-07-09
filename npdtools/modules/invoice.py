from datetime import datetime, timedelta
from typing import Literal

from npdtools.modules.base import NPDToolsBase
from npdtools.types.entity import ClientInfo
from npdtools.types.invoice import (
    BankAccount,
    BankPhone,
    Invoice,
    InvoicesList,
    PaymentOptions,
)
from npdtools.types.service import Service


class NPDToolsInvoice(NPDToolsBase):
    async def get_invoices(
        self,
        from_date: datetime | str | int = 7,
        to_date: datetime | str | int | None = None,
        offset: int = 0,
        limit: int = 10,
        sort_type: Literal["createdAt"] = "createdAt",
        is_sort_asc: bool = False,
    ) -> InvoicesList:
        if from_date is None:
            from_date: datetime = datetime.now()
        if isinstance(from_date, int):
            from_date: datetime = datetime.now() - timedelta(days=from_date)

        if isinstance(to_date, int):
            to_date: datetime = datetime.now() - timedelta(days=to_date)

        data = {
            "limit": limit,
            "offset": offset,
            "sorted": [{"id": sort_type, "desc": not is_sort_asc}],
            "filtered": [
                {
                    "id": "status",
                    "value": "ALL",
                },
                {
                    "id": "from",
                    "value": (
                        from_date
                        if isinstance(from_date, str)
                        else from_date.astimezone().isoformat()
                    ),
                },
                {
                    "id": "to",
                    "value": (
                        to_date
                        if isinstance(to_date, str)
                        else to_date.astimezone().isoformat()
                    ),
                },
            ],
        }
        response = await self._request(
            "POST",
            url="/invoice/table",
            json=data,
        )

        return InvoicesList(**response.json())

    async def create_invoice(
        self,
        *services: Service,
        bank: BankPhone | BankAccount,
        client: ClientInfo,
    ) -> Invoice:
        if client.name is None:
            raise ValueError(
                "Невозможно создать счёт, если не указано имя клиента (или название"
                " компании)"
            )

        data = {
            "clientType": str(client.type),
            "clientName": client.name,
            "type": "MANUAL",
            "services": [s.model_dump() for s in services],
            "totalAmount": str(sum(s.service_amount for s in services)),
        }

        if isinstance(bank, BankPhone):
            data["paymentType"] = "PHONE"
            data["bankName"] = bank.name
            data["phone"] = bank.phone
        elif isinstance(bank, BankAccount):
            data["paymentType"] = "ACCOUNT"
            data["bankName"] = bank.name
            data["bankBik"] = bank.bik
            data["corrAccount"] = bank.corr
            data["currentAccount"] = bank.account

        if client.inn is not None:
            data["clientInn"] = client.inn

        if client.phone is not None:
            data["clientPhone"] = client.phone

        if client.email is not None:
            data["clientEmail"] = client.email

        response = await self._request(
            "POST",
            url="/invoice",
            json=data,
        )

        return Invoice(**response.json())

    async def cancel_invoice(self, invoice_id: int) -> Invoice:
        response = await self._request(
            "POST",
            url=f"/invoice/{invoice_id}/cancel",
        )

        return Invoice(**response.json())

    async def invoice_paid(self, invoice_id: int) -> Invoice:
        response = await self._request(
            "POST",
            url=f"/invoice/{invoice_id}/approve",
        )

        return Invoice(**response.json())

    async def invoice_complete(
        self, invoice_id: int, operation_time: datetime | str = None
    ) -> Invoice:
        operation_time = (
            operation_time if operation_time is not None else datetime.now()
        )
        data = {
            "invoiceId": invoice_id,
            "requestTime": datetime.now()
            .replace(microsecond=0)
            .astimezone()
            .isoformat(),
            "operationTime": operation_time
            if isinstance(operation_time, str)
            else operation_time.now().replace(microsecond=0).astimezone().isoformat(),
        }
        response = await self._request(
            "POST",
            url=f"/invoice/{invoice_id}/receipt",
            json=data,
        )

        return Invoice(**response.json())

    async def update_invoice_payment_type(
        self, invoice_id: int, bank: BankPhone | BankAccount
    ) -> Invoice:
        data = {"invoiceId": invoice_id}

        if isinstance(bank, BankPhone):
            data["paymentType"] = "PHONE"
            data["bankName"] = bank.name
            data["phone"] = bank.phone
        elif isinstance(bank, BankAccount):
            data["paymentType"] = "ACCOUNT"
            data["bankName"] = bank.name
            data["bankBik"] = bank.bik
            data["corrAccount"] = bank.corr
            data["currentAccount"] = bank.account

        response = await self._request(
            "POST",
            url="/invoice/update-payment-info",
            json=data,
        )

        return Invoice(**response.json())

    async def get_payment_options(
        self, by_type: Literal["PHONE", "ACCOUNT"] | None = None
    ) -> PaymentOptions:
        response = await self._request(
            "GET",
            url="/payment-type/table",
            params={"type": by_type} if by_type else None,
        )

        return PaymentOptions(**response.json())
