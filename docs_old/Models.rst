Models
-----------------

Тут расположены примеры JSONов, с которыми приходится работать. Рассчитывай на объединение данных из запроса и ответа в объекте IncomeInfo

**Декларирование дохлда**

Запрос

::

  {
    "operationTime": "2021-05-14T06:07:27+03:00",
    "requestTime": "2021-05-14T06:07:27+03:00",
    "services": [
      {
        "name": "апавп",
        "amount": 44,
        "quantity": 1
      },
      {
        "name": "114",
        "amount": 12,
        "quantity": 1
      }
    ],
    "totalAmount": "56",
    "client": {
      "contactPhone": null,
      "displayName": "Rusalky Sosalky Davalky LLC",
      "inn": null,
      "incomeType": "FROM_FOREIGN_AGENCY"
    },
    "paymentType": "CASH",
    "ignoreMaxTotalIncomeRestriction": false
  }

Ответ

::

  {
    "approvedReceiptUuid":"201ggawqe9"
  }

=======

**Аннулирование чека**

Запрос

::

  {
    "operationTime": "2021-05-14T05:52:18+03:00",
    "requestTime": "2021-05-14T05:52:18+03:00",
    "comment": "Чек сформирован ошибочно",
    "receiptUuid": "201ggawqe9",
    "partnerCode": null
  }

Ответ

::

  {
    "incomeInfo": {
      "approvedReceiptUuid": "201ggawqe9",
      "name": "Носочки для детей розовые",
      "operationTime": "2021-05-06T02:46:39+03:00",
      "requestTime": "2021-05-06T02:46:39+03:00",
      "paymentType": "CASH",
      "partnerCode": "0",
      "totalAmount": 666,
      "cancellationInfo": {
        "operationTime": "2021-05-14T05:52:18+03:00",
        "registerTime": null,
        "taxPeriodId": null,
        "comment": "Чек сформирован ошибочно"
      },
      "sourceDeviceId": "16kcmyy1mq5i4wx61q5af"
    }
  }