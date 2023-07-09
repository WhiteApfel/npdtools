from decimal import Decimal


def amount_to_decimal(amount: int | float | str) -> Decimal:
    return Decimal(str(amount)).quantize(Decimal("0.00"))
