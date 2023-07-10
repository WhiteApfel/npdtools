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
        to_date: datetime | str | None = None,
        offset: int = 0,
        limit: int = 10,
        sort_type: Literal["createdAt"] = "createdAt",
        is_sort_asc: bool = False,
    ) -> InvoicesList:
        """
        Метод для получения списка счетов с учётом фильтров.

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_12)

        Args:
            from_date: Время начала поиск. Можно передать ``int``, тогда аргумент примет значение "``int`` дней назад", а время установится на ``0:00:00``
            to_date: Время окончания поиска. По умолчанию принимает значение ``datetime.now()``. Можно передать ``int``, тогда аргумент примет значение "``int`` дней назад", а время установится на ``23:59:59``
            offset: Сдвиг от начала найденных счетов (в т.ч. аннулированных)
            limit: Количество счетов в выдаче
            sort_type: Тип сортировки: только по дате, другие пока что не реализованы
            is_sort_asc: Сортировка по возрастанию?

        Returns:
            InvoicesList: Список счетов и сведения о пагинации
        """
        if from_date is None:
            from_date: datetime = datetime.now()
        if isinstance(from_date, int):
            from_date: datetime = (datetime.now() - timedelta(days=from_date)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

        if isinstance(to_date, int):
            to_date: datetime = (datetime.now() - timedelta(days=to_date)).replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )

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
        """
        Метод выставления счёта.

        На указанный ClientInfo.email должен отправиться чек после его формирования,
        но вообще не факт, что это произойдет.

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_11)

        Warning: Сведения о клиенте
            Для выставления счёта обязательно указать хоть какие-то сведения о контрагенте.

            Для физлиц обязательно указать ФИО. Инн, номер телефона и email по желанию

            Для юрлиц и ИП указать ИНН обязательно, остальное по желанию.

            Для иностранных компаний указать название обязательно.

        Примеры использования здесь: <<link>>

        Args:
            *services: Позиции в счёте: список товаров, услуг или подобного
            bank: Объект варианта приёма платежа: по номеру телефона или по реквизитам
            client: Объект сведений о клиенте

        Returns:
            Invoice: Полные сведения о счёте
        """
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
        """
        Метод для отмены счёта. Выданный к счёту чек не отменяется, вроде, его надо руками отменять.

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_11)

        Args:
            invoice_id: Номер счёта ``Invoice.invoice_id``

        Returns:
            Invoice: Актуальный полный объект счёта
        """
        response = await self._request(
            "POST",
            url=f"/invoice/{invoice_id}/cancel",
        )

        return Invoice(**response.json())

    async def invoice_paid(self, invoice_id: int) -> Invoice:
        """
        Метод, чтобы отметить счёт оплаченным. Чек можно выдать позже.

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_11)

        Args:
            invoice_id: Номер счёта ``Invoice.invoice_id``

        Returns:
            Invoice: Актуальный полный объект счёта
        """
        response = await self._request(
            "POST",
            url=f"/invoice/{invoice_id}/approve",
        )

        return Invoice(**response.json())

    async def invoice_complete(
        self, invoice_id: int, operation_time: datetime | str = None
    ) -> Invoice:
        """
        Метод для выдачи чека к счёту. Счёт автоматически становится оплаченным.

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_11)

        Args:
            invoice_id: Номер счёта ``Invoice.invoice_id``
            operation_time: Дата и время получения денег по счёту.

        Returns:
            Invoice: Актуальный полный объект счёта
        """
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
        """
        Метод для смены способа получения денег по счёту

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_11)

        Args:
            invoice_id: Номер счёта ``Invoice.invoice_id``
            bank: Сведения о способе получения денег. Можно создать руками или получить из ``NPDTools.get_payment_options()``

        Returns:
            Invoice: Актуальный полный объект счёта
        """
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
        """
        Метод для получения списка сохранённых способов получения денег по счёту

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_11)

        Args:
            by_type: Отфильтровать по типу способа получения

        Returns:
            PaymentOptions: Итерируемый объект со списком способов
        """
        response = await self._request(
            "GET",
            url="/payment-type/table",
            params={"type": by_type} if by_type else None,
        )

        return PaymentOptions(**response.json())
