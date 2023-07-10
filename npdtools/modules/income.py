from datetime import datetime, timedelta

from npdtools.modules.base import NPDToolsBase
from npdtools.types.entity import ClientInfo
from npdtools.types.income import CanceledIncome, IncomesList, NewIncome, SortTypes
from npdtools.types.service import Service


class NPDToolsIncome(NPDToolsBase):
    async def declare_income(
        self,
        *services: Service,
        client: ClientInfo | None = None,
        operation_time: datetime | str = None,
    ) -> NewIncome:
        """
        Метод для декларирования дохода. Иными словами, выдача чека.

        Notes: Список позиций чека
            Позиции чека передаются неименованными аргументами в количество 1+ штук. Вот пример:

            ```python
            services = [
                Service(name="Написание документации", amount=2500),
                Service(name="Настройка конфигов для документации", amount=1234.45, quantity=2),
                Service(name="Написание пайплайнов Gitlab CI", amount=Decimal("123.1")),
            ]
            service = Service(name="Капли для глаз", amount="12")

            await NPDTools.declare_income(*services)
            # or
            await NPDTools.declare_income(service, client=...)
            # or
            await NPDTools.declare_income(service, *services, client=...)
            ```

        Warning: Объект дохода
            Для получения полного объекта Income, следует обратиться к методу ``NPDTools.get_income(receipt_id=NewIncome.receipt_id)``

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_4)

        Args:
            *services: Позиции в чеке: список товаров, услуг или подобного
            client: Объект сведений о клиенте
            operation_time: Дата и время получения дохода.

        Returns:
            NewIncome: Объект нового дохода, **содержащий на данный момент только номер чека**,
        """
        client = client if client is not None else ClientInfo()

        operation_time = (
            operation_time if operation_time is not None else datetime.now()
        )
        data = {
            "paymentType": "CASH",
            "ignoreMaxTotalIncomeRestriction": False,
            "client": client.fns_export(),
            "requestTime": datetime.now()
            .replace(microsecond=0)
            .astimezone()
            .isoformat(),
            "operationTime": operation_time
            if isinstance(operation_time, str)
            else operation_time.now().replace(microsecond=0).astimezone().isoformat(),
            "services": [s.model_dump() for s in services],
            "totalAmount": str(sum(s.service_amount for s in services)),
        }

        response = await self._request(
            "POST",
            url="/income",
            json=data,
        )
        print(response.json())

        return NewIncome(**response.json())

    async def cancel_income(
        self,
        receipt_id: str,
        comment: str = "Чек сформирован ошибочно",
        cancellation_time: datetime | str | None = None,
    ) -> CanceledIncome:
        """
        Метод для аннулирования задекларированного дохода.

        [Примеры использования](https://npd-tools.readthedocs.io/en/dev/guide/example/#_9)

        Args:
            receipt_id: Номер чека. Те самые буквы-цифры.
            comment: Комментарий, по какой причине происходит аннулирование
            cancellation_time: Время отмены. Например, если вы вернули деньги вчера. По умолчанию принимает значение ``datetime.now()``

        Returns:
            CanceledIncome: Сведения об аннулированном доходе
        """
        cancellation_time = (
            cancellation_time if cancellation_time is not None else datetime.now()
        )

        data = {
            "comment": comment,
            "requestTime": datetime.now()
            .replace(microsecond=0)
            .astimezone()
            .isoformat(),
            "operationTime": cancellation_time
            if isinstance(cancellation_time, str)
            else cancellation_time.replace(microsecond=0).astimezone().isoformat(),
            "receiptUuid": receipt_id,
        }

        response = await self._request(
            "POST",
            url="/cancel",
            json=data,
        )

        return CanceledIncome(**response.json()["incomeInfo"])

    async def get_incomes(
        self,
        from_date: datetime | str | int = 7,
        to_date: datetime | str | int | None = None,
        offset: int = 0,
        limit: int = 10,
        sort_type: SortTypes | str = SortTypes.time,
        is_sort_asc: bool = False,
    ) -> IncomesList:
        """
        Метод для получения списка задекларированных доходов с учётом фильтров.

        Args:
            from_date: Время начала поиск. Можно передать ``int``, тогда аргумент примет значение "``int`` дней назад", а время установится на ``0:00:00``
            to_date: Время окончания поиска. По умолчанию принимает значение ``datetime.now()``. Можно передать ``int``, тогда аргумент примет значение "``int`` дней назад", а время установится на ``23:59:59``
            offset: Сдвиг от начала найденных доходов (в т.ч. аннулированных)
            limit: Количество доходов в выдаче
            sort_type: Тип сортировки: по дате или сумме
            is_sort_asc: Сортировка по возрастанию?

        Returns:
            IncomesList: Список доходов и сведения о пагинации
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

        params = {
            "from": (
                from_date
                if isinstance(from_date, str)
                else from_date.astimezone().isoformat()
            ),
            "to": (
                to_date
                if isinstance(to_date, str)
                else to_date.astimezone().isoformat()
            ),
            "offset": offset,
            "sortBy": f'{str(sort_type)}:{"asc" if is_sort_asc else "desc"}',
            "limit": limit,
        }
        response = await self._request(
            "GET",
            "/invoices",
            params=params,
        )

        return IncomesList(**response.json())
