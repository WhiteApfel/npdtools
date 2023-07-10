from _decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from npdtools.helpers import amount_to_decimal


class Service(BaseModel):
    """
    Объект позиции в чеке или счёте

    Attributes:
        name: Название позиции: товара, услуги или подобного
        amount: Цена единицы позиции. За штуку, грамм или подобное
        quantity: Количество. Штук, грамм или подобного
        number: Порядковый номер позиции. Техническая штука.
    """

    name: str
    amount: Decimal
    quantity: int = 1
    number: int | None = Field(None, alias="serviceNumber", exclude=True)

    @field_validator("amount", mode="before")
    @classmethod
    def amount_normalize(cls, value: int | float | str | Decimal):
        return amount_to_decimal(value)

    @property
    def service_amount(self) -> Decimal:
        """
        Returns:
            Decimal: Стоимость всей позиции. Цена умножить на количество.
        """
        return self.amount * self.quantity
