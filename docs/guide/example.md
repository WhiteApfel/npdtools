# Примеры использования

**Во всех примерах, кроме авторизации, опущены инициализация и запуск. Лишь функция example**

## Авторизация

```python
from asyncio import run
from decimal import Decimal

from npdtools import NPDTools
from npdtools.types import Service, ClientType, ClientInfo

npd = NPDTools()


async def example(client: NPDTools):
    ...


async def main(client: NPDTools):
    await client.auth("123456789012", "~_ub&TS5RY~k9,czo(q*")
    await example(client)

    
run(main())

```

## Чеки

### Декларация дохода / Выдача чека

#### Добавление позиций в чек

```python
from npdtools.types import Service
from npdtools import NPDTools

from decimal import Decimal

async def example(client: NPDTools):
    # Как добавлять позиции в чек:
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    cart.append(Service(name="Прокладкохолдер", amount=1234.56))
    await client.declare_income(*cart)

    # Вот так можно декларировать товары на развес: с ценой за грамм и указанием веса в граммах
    await client.declare_income(Service(name="Изюм", amount=Decimal("0.4"), quantity=856))
```

#### Выдача чека физлицу

```python
from npdtools.types import ClientInfo, ClientType, Service
from npdtools import NPDTools

async def example(client: NPDTools):
    # Применяется автоматически, так как никакие данные не требуются
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    await client.declare_income(*cart)

    # Если хотите выдать чек физлицу с указанием его фио, телефона, ИНН или иных данных
    client_info = ClientInfo(
        type=ClientType.individual,  # это не обязательно, так как ``individual`` - значение по умолчанию
        inn="012345678912",  # Как и поля ниже, можно указывать, если знаем, либо пропустить (или передать None)
        name="Зотов Данил Константинович",
        phone="79998887766",  # Допускается любой формат
        email="i@mhorny.gay",  # Туда может приходить чек от ФНС, но не факт
    )
    await client.declare_income(*cart, client=client_info)
```

#### Выдача чека российской организации или ИП

```python
from npdtools.types import ClientInfo, ClientType, Service
from npdtools import NPDTools

async def example(client: NPDTools):
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    client_info = ClientInfo(
        type=ClientType.legal,  # Указывает на то, что чек для компании или ИП
        inn="012345678912",  # Надо указать ИНН. Обязательно.
        name="ИП Колосов Илья Владимирович",  # Краткое название, указывать не обязательно, но желательно
        phone="79998887766",  # Контактный номер по желанию
        email="i@mhorny.gay",  # Контактный email по желанию
    )
    await client.declare_income(*cart, client=client_info)
```

#### Выдача чека иностранным организации или физлицу

```python
from npdtools.types import ClientInfo, ClientType, Service
from npdtools import NPDTools

async def example(client: NPDTools):
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    client_info = ClientInfo(
        type=ClientType.foreign,  # Указывает, что получатель не является налоговым резидентом РФ
        # inn="012345678912",  # ИНН можно указать, если он известен
        name="Rusalky Sosalky Davalky Inc.",  # Краткое название, указывать не обязательно, но желательно
        phone="+13053056699",  # Контактный номер по желанию
        # email="i@mhorny.gay",  # Контактный email по желанию
    )
    await client.declare_income(*cart, client=client_info)
```

### Отмена / Аннулирование

**Канселим чеки, как Италию на Евровидении 2021**

```python
from datetime import datetime, timedelta

from npdtools import NPDTools
from npdtools.types import Service


async def example(client: NPDTools):
    # Выдаём чек
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    declare_response = await client.declare_income(*cart)
    
    # Отменяем его
    await client.cancel_income(declare_response.receipt_id)

    # С комментарием:
    await client.cancel_income(declare_response.receipt_id, comment="Этот мудень попросил вернуть деньги")

    # Возврат за вчерашний день
    await client.cancel_income(declare_response.receipt_id, comment="Не подошёл размер", cancellation_time=datetime.now() - timedelta(days=1))
```

### Счета

#### Работа со счётом

```python
from npdtools import NPDTools
from npdtools.types import Service, BankAccount, BankPhone, ClientInfo, ClientType


async def example(client: NPDTools):
    # Получаем список сохранённых способов получения денег
    options = await client.get_payment_options()
    if len(options) == 0:  # Если нет сохранённых
        # Создаём объект сами
        # По СБП
        payment_option = BankPhone(
          name="Банк Хaйс",
          phone="79998887766",
        )
        # Или
        # По реквизитам счёта
        payment_option = BankAccount(
          name="Точка Банк",
          bik="044525104",
          account="40802810201500127107",
          corr="30101810745374525104",
        )
    else:
        # Используем первый попавшийся, но можно выбрать по параметрам руками
        payment_option = options[0]
    
    # Для физлица обязательно указать ФИО 
    # Для ИП и ООО - ИНН
    # Для зарубежных - название (тоже поле ``name``)
    client_info = ClientInfo(
      name="Карасуков Владимир Ярославович",
      type=ClientType.individual,  # Для ИП, ООО и зарубежных указать свой тип
      phone="79998887766",  # Необязательно
      email="i@mhorny.gay",  # Необязательно. На этот адрес может прийти чек после его выдачи
    )

    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    invoice = await client.create_invoice(
        *cart,
        bank=payment_option,
        client=client_info,
    )
    
    # Сменим способ получения денег
    invoice = await client.update_invoice_payment_type(
        invoice_id=invoice.invoice_id,
        bank=BankPhone(
          name="Банк Хaйс",
          phone="79998887766",
        ),
    )
    # Отметим счёт оплаченным
    invoice = await client.invoice_paid(invoice.invoice_id)
    # Выдадим чек по этому счёту
    invoice = await client.invoice_complete(invoice.invoice_id)
    # Аннулируем счёт
    invoice = await client.cancel_invoice(invoice.invoice_id)
    # Не забудем и чек аннулировать!
    canceled_income = await client.cancel_income(receipt_id=invoice.receipt_id)
```

### Получение списка счетов

```python
from npdtools import NPDTools

from datetime import datetime, timedelta


async def example(client: NPDTools):
    # За последние 7 дней
    invoices = await client.get_invoices(from_date=7)

    # за прошлый месяц
    now = datetime.now()
    this_first = now.replace(day=1)
    prev_last = this_first - timedelta(days=1)
    prev_first = prev_last.replace(day=1)
    
    prev_first = prev_first.replace(hour=0, minute=0, second=0, microsecond=0)
    prev_last = prev_last.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Чтобы получить все, может потребоваться несколько обращений
    all_invoices = []
    offset = 0
    limit = 10
    
    while True:
        invoices = await client.get_invoices(
            from_date=prev_first,
            to_date=prev_last,
            offset=offset,
            limit=limit,
            is_sort_asc=True, # Хотим получать от старых к новым, не как обычно
        )
        
        all_invoices.extend(invoices)
        
        if not invoices.has_more:
            break
        
        limit = invoices.limit  # Иногда ФНС меняет limit, поэтому так
        offset = invoices.offset + limit  # По той же причине смотрим offset в ответе ФНС
```