
from aiohttp import (
    ClientSession,
    ClientTimeout,
    ClientResponseError,
    ClientConnectionError,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    retry_if_result
)

from decorators import validations

class Api:
    DEFAULT_TIMEOUT = 5
    RETRY_ATTEMPTS = 2
    RETRY_BACKOFF = 0.7

    def __init__(self, rest_url: str, test_endpoint: str = "api/"):
        if not rest_url:
            raise ValueError("REST URL must be provided for Api instance.")

        self.__session: ClientSession = None
        self.__url = rest_url.rstrip("/")
        self.__test_endpoint = test_endpoint
        self.__timeout = ClientTimeout(total = self.DEFAULT_TIMEOUT)

        try:
            self.connect()
        except Exception as e:
            raise ConnectionError(f"Client session could not be established: {e}") from e

        self.guild = self.__Guild(self)

    def connect(self):
        self.__session = ClientSession(timeout = self.__timeout)

    async def close(self):
        if self.__session:
            await self.__session.close()
            self.__session = None

    async def test(self):
        return await self._request("GET", self.__test_endpoint)

    def _is_retryable(self, exc_or_resp):
        if isinstance(exc_or_resp, (ClientConnectionError, TimeoutError)):
            return True
        if isinstance(exc_or_resp, ClientResponseError):
            return exc_or_resp.status in (502, 503, 504)

        if hasattr(exc_or_resp, 'status'):
            return exc_or_resp.status in (502, 503, 504)
        return False

    def _retry_predicate(self, exc):
        return self._is_retryable(exc)

    @retry(
        stop = stop_after_attempt(RETRY_ATTEMPTS + 1),
        wait = wait_fixed(RETRY_BACKOFF),
        retry = (
            retry_if_exception_type((
                ClientConnectionError,
                TimeoutError,
                ClientResponseError
            ))
            .__or__(retry_if_result(
                lambda resp: hasattr(resp, 'status') and resp.status in (502, 503, 504)
            ))
        ),
        reraise = True
    )
    async def _request(self, method: str, endpoint: str, /, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.__timeout

        try:
            async with self.__session.request(
                method,
                f"{self.__url}/{endpoint}",
                **kwargs
            ) as response:
                response.raise_for_status()
                return await response.json()

        except (ClientConnectionError, TimeoutError, ClientResponseError) as exc:
            if self._is_retryable(exc):
                raise
            raise

    class __Guild:
        def __init__(self, parent):
            self.__parent: Api = parent
            self.__endpoint = "api/bot/guild/"

        @validations.args_required([("id", int)])
        async def get(self, id: int):
            return await self.__parent._request("GET", f"{self.__endpoint}{id}")
        
        @validations.args_required([
            ("id", int),
            ("name", str)
        ])
        async def post(self, id: int, name: str):
            return await self.__parent._request("POST", self.__endpoint, json = {
                "id": id,
                "name": name
            })
        
        @validations.args_required([("id", int)])
        async def patch(self, id: int, /, *, 
            name: str = None,
            lang: str = None
        ):
            json = {}
            if name is not None: json["name"] = name
            if lang is not None: json["lang"] = lang
            return await self.__parent._request("PATCH", f"{self.__endpoint}{id}", json = json)
        
        @validations.args_required([("id", int)])
        async def delete(self, id: int):
            return await self.__parent._request("DELETE", f"{self.__endpoint}{id}")
