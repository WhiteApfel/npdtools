from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Callable

import dateutil.parser


class TokenField(str):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, args[0])

    def __init__(
        self, value, *, expires_in: int | None = None, expires: datetime | None = None
    ):
        if expires is not None:
            self.expires = expires
        elif expires_in is None:
            self.expires = None
        else:
            self.expires = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in - 10
            )

    @property
    def is_alive(self) -> bool:
        if self.expires is None:
            return True
        return datetime.now(timezone.utc) < self.expires


class TokenDescriptor:
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner) -> TokenField | None:
        return self.value

    def __set__(
        self, instance, value: tuple[str, int | datetime | None, datetime | None] | str
    ):
        if type(value) is str:
            value = (value, None, None)
        elif len(value) == 1:
            value = value + (None, None)
        elif isinstance(value[1], datetime):
            value = (value[0], None, value[1])
        elif len(value) == 2:
            value = value + (None,)
        self.value = TokenField(value[0], expires_in=value[1], expires=value[2])

        instance.on_update(instance.inn, instance)


class Tokens:
    __slots__ = ("on_update", "inn")
    token_fields = ("device", "access", "refresh")
    device: TokenField | None = TokenDescriptor()
    access: TokenField | None = TokenDescriptor()
    refresh: TokenField | None = TokenDescriptor()

    def __init__(self, inn, on_update: Callable[[str, dict], None]):
        self.on_update = on_update
        self.inn = inn

    def dump(self) -> tuple[str, dict]:
        data = {}

        for field_name in self.token_fields:
            if field_name[0] == "_":
                continue

            field = getattr(self, field_name, None)

            data[field_name] = {
                "value": field,
                "expires": field.expires if field else None,
            }

        return self.inn, data

    def load(self, inn: str, data: dict[str, dict[str, str | datetime | None]]):
        self.inn = inn
        if not all(field in data for field in self.token_fields):
            raise ValueError("data does not contain all fields")

        for field_name in self.token_fields:
            field_data = data.get(field_name)
            value = field_data.get("value")
            expires = field_data.get("expires")
            if isinstance(expires, str):
                expires = dateutil.parser.parse(expires)
            setattr(self, field_name, (value, None, expires))


class AbstractTokenManager(ABC):
    def __init__(self, **kwargs):
        ...

    @abstractmethod
    def on_update(self, inn: str, tokens_data: Tokens) -> None:
        ...

    @abstractmethod
    def get_tokens(self, inn: str, **kwargs) -> Tokens:
        ...

    @abstractmethod
    def load_tokens(self, **kwargs):
        ...


class InMemoryTokenManager(AbstractTokenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tokens_mapper: dict[str, Tokens] = {}

    def on_update(self, inn: str, tokens_data: Tokens) -> None:
        pass

    def get_tokens(self, inn: str, **kwargs) -> Tokens:
        return self.tokens_mapper.setdefault(inn, Tokens(inn, self.on_update))

    def load_tokens(self, **kwargs):
        pass
