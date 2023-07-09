from datetime import datetime, timedelta

from npdtools.modules.base import NPDToolsBase
from npdtools.types.entity import ClientInfo
from npdtools.types.income import (
    AddIncomeInfo,
    CancellationIncome,
    IncomesList,
    SortTypes,
)
from npdtools.types.service import Service


class NPDToolsIncome(NPDToolsBase):
    async def declare_income(
        self,
        *services: Service,
        client: ClientInfo | None = None,
        operation_time: datetime | str = None,
    ):
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

        if response.is_success:
            return AddIncomeInfo(**response.json())

    async def cancel_income(
        self,
        receipt_id: str,
        comment: str = "Чек сформирован ошибочно",
        cancellation_time: datetime | None = None,
    ) -> CancellationIncome:
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

        print(response.json())
        return CancellationIncome(**response.json()["incomeInfo"])

    async def get_incomes(
        self,
        from_date: datetime | str | int = 7,
        to_date: datetime | str | int | None = None,
        offset: int = 0,
        limit: int = 10,
        sort_type: SortTypes | str = SortTypes.time,
        is_sort_asc: bool = False,
    ) -> IncomesList:
        if from_date is None:
            from_date: datetime = datetime.now()
        if isinstance(from_date, int):
            from_date: datetime = datetime.now() - timedelta(days=from_date)

        if isinstance(to_date, int):
            to_date: datetime = datetime.now() - timedelta(days=to_date)

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
