# NPDTools

Ищешь инструмент для удобного декларирования доходов? 
Хочешь автоматизировать выдачу чеков клиентам?
Надоело заходить в Мой налог? Надоедает проверять, что каждый приход зарегистрирован в налоговой?
Боишься ошибиться и получить безжалостный удар от ФНС кнутом без пряника?

### ВЫХОД ЕСТЬ! Для этого потребуется простая питоняшая...

Нет, не сода. Либа. README которой ты сейчас читаешь. 
Да, она позволяет работать с API Федеральной налоговой службы (ФНС) в рамках возможностей
приложения "Мой налог". Больше она не умеет. Столько же не умеет. Меньше умеет.
Надеюсь, теперь все люди, что искали подобный инструмент в гугле, смогли его найти.
Можно приступить к содержательной части. 

## Если ты не знаешь свой ⚠️ password ⚠️

Если входишь в lknpd.nalog.ru или "Мой налог" через Госуслуги (ЕСИА) или просто не помнишь пароль,
надо зайти на [lkfl2.nalog.ru](https://lkfl2.nalog.ru 'Личный кабинет физлица') и там по ситуации:
* Войти так же через Госуслуги и сменить (установить) пароль в настройках профиля
* Войти по электронной подписи и сменить пароль в настройках профиля
* Нажать кнопочку "Восстановить пароль" и пройти процедуру восстановления
* Не разобраться в ситуации и смириться со сложностью бытия

## Прогресс разработки
* Чеки
  * [x] Создание чека
  * [x] Аннулирование чека
  * [x] Получение списка чеков
* Счета
  * [x] Создание счёта
  * [x] Отметка оплаченным
  * [x] Выдача чека по счёту
  * [x] Смена способа оплаты
  * [x] Отмена счёта
  * [x] Получение способов оплаты счёта
* Публичное
  * [ ] Проверка статуса самозанятого
  * [ ] Проверка чеков по токену
  * [ ] Проверка налогов по токену
  * [ ] Проверка оплат налогов по токену
* Другое
  * [ ] Добавление способа оплаты счёта
  * [ ] Удаление способа оплаты счёта
  * [ ] Активация и деактивация автоплатежа
  * [ ] Удаление привязанной карты для автоплатежа
  * [ ] Изменение видов деятельности
  * [ ] Редактирование профессии
  * [ ] Редактирование текста в чеке
  * [ ] Удаление партнёров
  * [ ] Снятие с учёта НПД
  * [ ] Отображение номера и почты в чеке
  * [ ] Ключи доступа
  * [ ] Справки

  
## Документация

Её в нормальном виде нет, но в коде описано детально, какие модели возвращает функция, можно смотреть на них.
Когда-нибудь, возможно, добавлю больше.

## Что может библиотека?

Собственно, всё сводится к выставлению, закрытию и получению счетов и чеков.
Что? Примеров хочешь? Держи примеров. Обмажься. 

### Выставляем чек, как профи

```python
from decimal import Decimal

from npdtools import NPDTools
from npdtools.types import Service, ClientType, ClientInfo

client = NPDTools(default_inn="123456789012")


async def main():
    await client.auth("123456789012", "~_ub&TS5RY~k9,czo(q*")

    # Как добавлять позиции в чек:
    # 1. Метод здорового человека
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    cart.append(Service(name="Прокладкохолдер", amount=1234.56))
    await client.declare_income(*cart)

    # Вот так можно декларировать товары на развес: с ценой за грамм и указанием веса в граммах
    await client.declare_income(Service(name="Изюм", amount=Decimal("0.4"), quantity=856))

    # 2. Метод немного здорового человека
    await client.declare_income(Service(name="Доска", amount=600, quantity=2), Service(name="Udjplb", amount=4, quantity=10))

    # Как выставлять физлицам?
    # Применяется автоматически, так как никакие данные не требуются
    await client.declare_income(*cart)

    # Если хотите выдать чек физлицу с указанием его фио, телефона, инн или иных данных
    client_info = ClientInfo(
        type=ClientType.individual,  # это не обязательно, так как значение по умолчанию
        inn="012345678912",  # Как и поля ниже, можно указывать, если знаем, либо пропустить (или передать None)
        name="Зотов Данил Константинович",
        phone="79998887766",  # Допускается любой формат
        email="i@mhorny.gay",  # Туда может приходить чек от ФНС, но не факт
    )
    await client.declare_income(*cart, client=client_info)

    # ИП или ООО или прочая российская организация?
    client_info = ClientInfo(
        type=ClientType.legal,  # это не обязательно, так как значение по умолчанию
        inn="012345678912",  # Для ИП и ООО надо указать ИНН. Обязательно.
        name="ИП Колосов Илья Владимирович",  # Краткое название, указывать не обязательно, но желательно
        phone="79998887766",  # Контактный номер по желанию
        # email="i@mhorny.gay",  # Контактный email по желанию
    )
    await client.declare_income(*cart, client=client_info)

    # Если организация иностранная?
    client_info = ClientInfo(
        type=ClientType.foreign,  # это не обязательно, так как значение по умолчанию
        # inn="012345678912",  # ИНН можно указать, если он известен
        name="Rusalky Sosalky Davalky Inc.",  # Краткое название, указывать не обязательно, но желательно
        phone="+13053056699",  # Контактный номер по желанию
        # email="i@mhorny.gay",  # Контактный email по желанию
    )
    await client.declare_income(*cart, client=client_info)
```

### Канселим чеки, как Италию на Евровидении 2021

```python
from datetime import datetime, timedelta

from npdtools import NPDTools
from npdtools.types import Service

client = NPDTools(default_inn="123456789012")


async def main():
    await client.auth("123456789012", "~_ub&TS5RY~k9,czo(q*")
    
    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    await client.declare_income(*cart)

    declare_response = await client.declare_income(*cart)
    await client.cancel_income(declare_response.receipt_id)

    # С комментарием:
    await client.cancel_income(declare_response.receipt_id, comment="Этот мудень попросил вернуть деньги")

    # Возврат за вчерашний день
    await client.cancel_income(declare_response.receipt_id, comment="Не подошёл размер", cancellation_time=datetime.now() - timedelta(days=1))
```

### Счета
```python
from npdtools import NPDTools
from npdtools.types import Service, BankAccount, BankPhone, ClientInfo, ClientType

client = NPDTools(default_inn="123456789012")


async def main():
    await client.auth("123456789012", "~_ub&TS5RY~k9,czo(q*")
    options = await client.get_payment_options()
    if len(options) == 0:
        # По СБП
        payment_option = BankPhone(
          name="Банк Хaйс",
          phone="79998887766",
        )

        # По реквизитам счёта
        payment_option = BankAccount(
          name="Точка Банк",
          bik="044525104",
          account="40802810201500127107",
          corr="30101810745374525104",
        )
    else:
        payment_option = options[0]
    
    # Для физлица обязательно указать ФИО. Для ИП и ООО - ИНН. Для зарубежных - название (тоже name)
    client_info = ClientInfo(
      name="Карасуков Владимир Ярославович",
      type=ClientType.individual,  # Для ИП, ООО и зарубежных указать свой тип
      phone="79998887766",  # Необязательно
      email="i@mhorny.gay",  # На этот адрес должен будет прийти чек после его выдачи, необязательно
    )

    cart = [Service(name="Прокладка с крылышками", amount=180.85, quantity=2)]
    invoice = await client.create_invoice(
        *cart,
        bank=payment_option,
        client=client_info,
    )

    invoice = await client.invoice_paid(invoice.invoice_id)
    invoice = await client.invoice_complete(invoice.invoice_id)
    # or
    invoice = await client.cancel_invoice(invoice.invoice_id)
```
Я буду ещё дописывать библиотеку, да. Но пока так. Она не такая простая, как кажется.

Буду рад конструктивным пул реквестам и иссуям.