from datetime import datetime
from random import choice
from string import ascii_lowercase, digits
from typing import Literal, Type

import ujson as ujson
from httpx import AsyncClient, Response

from npdtools.settings import DATE_FORMAT, HTTP_TIMEOUT, LKNPD_API_V1
from npdtools.token_manager import AbstractTokenManager, InMemoryTokenManager


class NPDToolsBase:
    def __init__(
        self,
        token_manager: Type[AbstractTokenManager] = InMemoryTokenManager,
        default_inn: str | None = None,
        base_url: str | None = None,
        http_session: AsyncClient = None,
        *args,
        **token_manager_data,
    ):
        """

        Args:
            token_manager:
            default_inn:
            base_url:
            http_session:
            *args:
            **token_manager_data:
        Attributes:

        """
        self._base_url = LKNPD_API_V1 if not base_url else base_url
        self._http_session: AsyncClient = http_session

        self._default_inn: str | None = default_inn
        self.token_manager: AbstractTokenManager = token_manager(**token_manager_data)
        self.token_manager.load_tokens()

        self._device_id_factory = lambda: "".join(
            [choice(ascii_lowercase + digits) for _ in range(21)]
        )

    @property
    def http_session(self) -> AsyncClient:
        if self._http_session is None:
            self._http_session = AsyncClient(timeout=HTTP_TIMEOUT)
        return self._http_session

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        url: str = "/",
        data: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        cookies: dict | None = None,
        content: bytes | None = None,
        referer: str | None = None,
        auth_required: bool = True,
        inn: str | None = None,
        **get_tokens_params,
    ) -> Response:
        headers = headers or {}
        if json is not None:
            content = ujson.encode(json)
            headers |= {"Content-Type": "application/json"}
        if auth_required:
            if self._default_inn:
                get_tokens_params = get_tokens_params | {
                    "inn": inn or self._default_inn
                }
            tokens = self.token_manager.get_tokens(**get_tokens_params)
            if (
                tokens.access is not None
                and not tokens.access.is_alive
                and tokens.refresh is not None
            ):
                await self.auth(refresh_token=tokens.refresh)
            elif tokens.access is None or tokens.refresh is None:
                raise ValueError("access_token is needed for authorization")
            headers |= {"Authorization": f"Bearer {tokens.access}"}

        headers = {
            "referer": f'https://lknpd.nalog.ru/{referer if referer else ""}'
        } | headers

        return await self.http_session.request(
            method=method,
            url=url if url.startswith("https://") else self._base_url + url,
            data=data,
            headers=headers,
            params=params,
            cookies=cookies,
            content=content,
        )

    async def auth(
        self,
        inn: str = None,
        password: str = None,
        refresh_token: str = None,
        device_id: str | None = None,
        **get_tokens_params,
    ):
        inn = inn or self._default_inn
        if inn is None:
            ValueError()  # TODO: add info

        tokens = self.token_manager.get_tokens(inn, **get_tokens_params)
        if tokens.device is None:
            tokens.device = (
                device_id if device_id is not None else self._device_id_factory()
            )

        if password is not None:
            tokens = self.token_manager.get_tokens(inn)

        auth_data = {
            "deviceInfo": {
                "appVersion": "1.0.0",
                "sourceDeviceId": tokens.device,
                "sourceType": "WEB",
                "metaDetails": {
                    "userAgent": (
                        "Mozilla/5.0 (X11; rv:109.0) Gecko/20100101 Firefox/109.0"
                        " npdtools"
                    )
                },
            },
        }

        if refresh_token is not None:
            auth_data |= {
                "refresh_token": refresh_token,
            }
        else:
            auth_data |= {
                "username": inn,
                "password": password,
            }

        response = await self._request(
            method="POST",
            url="/auth/token" if refresh_token is not None else "/auth/lkfl",
            json=auth_data,
            headers={"referer": f"https://lknpd.nalog.ru/Sales"},
            auth_required=False,
        )

        r_data = response.json()
        tokens.access = r_data["token"], datetime.strptime(
            r_data["tokenExpireIn"].replace("Z", "+00:00"),
            DATE_FORMAT,
        )
        tokens.refresh = r_data["refreshToken"]

        return response
