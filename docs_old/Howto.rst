How to use
==========

Как использовать? Хороший вопрос. Примерно так.

::

  from npdtools import NPDTools
  from npdtools.types import Services

  client = NPDTools("54082336174", "p@s$vv0Rd")

  services = Services()
  services.add("Изюм", 350, 2) # 350 рублей за условный килограмм, 2 килограмма
  services.add("Пакет", 4.55, 1) # один пакет за 4.55 рублей

  print(services.total_amount)

  income = client.add_income(services)

  cancelled = client.cancel_income(income.id)

  print(cancelled.cancellation_info)