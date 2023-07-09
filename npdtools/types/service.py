from _decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from npdtools.helpers import amount_to_decimal


class Service(BaseModel):
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
        return self.amount * self.quantity
