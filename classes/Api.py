from time import perf_counter
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
    retry_if_exception,
)
from jwt import decode as jwt_decode
from asyncio import Lock as AsyncLock
from datetime import datetime, timezone

from utils.funcs import (
    normalize_url,
    id_url_param,
)
from utils.logger import logger

class _ApiClient:
    r"""
    A client for making HTTP requests to a RESTful API, with built-in retry logic for handling transient errors.

    Args:
        path (str): The base URL for the API.
        session (ClientSession, optional): An optional aiohttp ClientSession to use for making requests. If not provided, a new session will be created when needed.
        add_slash (bool, optional): Whether to ensure that the base URL ends with a slash. Defaults to True.

    Example:
    ```
        api = _ApiClient("http://example.com/api")

        await api.get("users")
        await api.post("users", json = {"name": "Alice"})
        await api.patch("users/1", json = {"name": "Alice Smith"})
        await api.delete("users/1")

        api.close()
    ```
    """

    DEFAULT_TIMEOUT = 5
    RETRY_ATTEMPTS = 2
    RETRY_BACKOFF = 0.7

    def __init__(self, path: str, /, *,
        session: ClientSession = None,
        add_slash: bool = True,
    ):
        self.path = normalize_url(path, "", trailing_slash = add_slash)
        
        self._use_slash = add_slash

        self._session = session
        self._timeout = ClientTimeout(total = self.DEFAULT_TIMEOUT)
        
        self._token = None
        self._refreshing_token = None
        self._expire_at = 0
        self._refresh_lock = AsyncLock()

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout = self._timeout)

        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @staticmethod
    def _is_retryable(exc):
        if isinstance(exc, (ClientConnectionError, TimeoutError)):
            return True
        
        if isinstance(exc, ClientResponseError):
            return exc.status in (502, 503, 504)
        
        return False

    def set_tokens(self, access_token: str, refresh_token: str):
        self._token = access_token
        self._refreshing_token = refresh_token

        if not access_token:
            self._expire_at = 0
            return

        try:
            payload = jwt_decode(access_token, options={"verify_signature": False})
            self._expire_at = payload.get("exp", 0)
        except Exception as e:
            logger.error("Failed to decode access token for expiration time", exc_info=e)

            self._expire_at = 0

    async def refresh_handler(self):
        """ This method is assigned from ApiServices initialization to handle token refresh/re-auth """

        pass

    async def _handle_refresh(self):
        try:
            await self.refresh_handler()
        except ClientResponseError as e:
            if e.status in (400, 401, 403):
                logger.warning("Refresh token expired or invalid, attempting full re-authentication callback")
                await self.refresh_handler()
            else:
                raise e

    @retry(
        stop = stop_after_attempt(RETRY_ATTEMPTS + 1),
        wait = wait_fixed(RETRY_BACKOFF),
        retry = retry_if_exception(lambda exc: _ApiClient._is_retryable(exc)),
        reraise = True
    )
    async def _request(self, method: str, endpoint: str, /, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self._timeout

        headers = kwargs.get("headers", {})
        headers["X-Source"] = "bot"

        if self._token and "auth/token" not in endpoint:
            now = datetime.now(timezone.utc).timestamp()
            if self._expire_at - now < 30:
                async with self._refresh_lock:
                    await self._handle_refresh()

            headers["Authorization"] = f"Bearer {self._token}"
        
        kwargs["headers"] = headers

        path = normalize_url(self.path, endpoint, trailing_slash = self._use_slash)

        async with self.session.request(method, path, **kwargs) as response:
            if response.status == 204:
                return None

            response.raise_for_status()
            return await response.json()

    async def get(self, endpoint: str, /, **kwargs):
        return await self._request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, /, **kwargs):
        return await self._request("POST", endpoint, **kwargs)
    
    async def patch(self, endpoint: str, /, **kwargs):
        return await self._request("PATCH", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, /, **kwargs):
        return await self._request("DELETE", endpoint, **kwargs)    

class _ApiInterface:
    r"""
    A base class for API service interfaces, providing common functionality for constructing endpoint URLs and making requests through an _ApiClient instance.

    Args:
        client (_ApiClient): An instance of the _ApiClient class to use for making requests.
        endpoint (str): The base endpoint for the API service (e.g., "users").

    Properties:
        client (_ApiClient): The _ApiClient instance used for making requests.
        endpoint (str): The base endpoint for the API service.
        url (str): The full URL for the API service, constructed from the client's base path and the service's endpoint.

    Methods:
        get(id: int = 0): Make a GET request to the service's endpoint, optionally with an ID parameter.
        new(*args, **kwargs): An abstract method that must be implemented by subclasses to create new resources through the API.

    Example:
    ```
        class MyService(_ApiInterface):
            # Initialize the service with the client and endpoint
            def __init__(self, client: _ApiClient, endpoint: str):
                super().__init__(client, endpoint)

            # Implement the abstract new method to create a new resource
            async def new(self):
                return await self.client.post(self.endpoint, json = {"key": "value"})
                
            # you can add more methods for other operations
            async def my_custom_method(self):
                return await self.client.get(f"{self.endpoint}/custom")

        my_service = MyService(_ApiClient("http://example.com/api"), "myservice")

        my_service.endpoint  # "myservice"
        my_service.url       # "http://example.com/api/myservice/"

        await my_service.get()               # Makes a GET request to "http://example.com/api/myservice/"
        await my_service.new()               # Calls the new method to create a new resource
        await my_service.my_custom_method()  # Calls the custom method for additional operations   
    ```
    """

    def __init__(self, client: _ApiClient, endpoint: str):
        self._client = client
        self._endpoint = endpoint

    @property
    def client(self):
        return self._client

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def url(self):
        return normalize_url(self._client.path, self._endpoint,
            trailing_slash = self._client._use_slash
        )

    async def get(self, id: int = 0):
        return await self._client.get(
            normalize_url(self.endpoint, id_url_param(id),
                trailing_slash = self._client._use_slash
            )
        )

class _Tokens(_ApiInterface):
    def __init__(self, client: _ApiClient, /, *,
        endpoint: str = "auth/token"
    ):
        super().__init__(client, endpoint)
    
    def _set_tokens(self, data: dict):
        self.client.set_tokens(
            data.get("access"),
            data.get("refresh")
        )

    async def get(self, username: str, password: str):
        self._set_tokens(
            await self.client.post(self.endpoint, json = {
                "username": username,
                "password": password,
            })
        )

    async def refresh(self):
        self._set_tokens(
            await self.client.post(
                normalize_url(self.endpoint, "refresh", trailing_slash = self.client._use_slash),
                json = {"refresh": self.client._refreshing_token}
            )
        )

class _Guild(_ApiInterface):
    def __init__(self, client: _ApiClient, /, *,
        endpoint: str = "api/guilds"
    ):
        super().__init__(client, endpoint)
    
    async def new(self, id: int):
        return await self.client.post(self.endpoint, json = {
            "id": id
        })

    async def update(self, id: int, **kwargs):
        return await self.client.patch(
            normalize_url(self.endpoint, id_url_param(id),
                trailing_slash = self.client._use_slash
            ),
            json = kwargs
        )
    
    async def delete(self, id: int):
        return await self.client.delete(
            normalize_url(self.endpoint, id_url_param(id),
                trailing_slash = self.client._use_slash
            )
        )

class ApiServices:
    def __init__(self, path: str, /, *,
        session: ClientSession = None,
        add_slash: bool = True,
    ):
        self._client = _ApiClient(path,
            session = session,
            add_slash = add_slash
        )

        self.guild = _Guild(self._client)
        self.tokens = _Tokens(self._client)

        self._client.refresh_handler = self.tokens.refresh

    async def ping(self) -> float:
        """ Measure the latency of the API by sending a HEAD request to the base URL. """

        start_time = perf_counter()
        url = f"{self._client.path}api/health/"
        try:
            async with self._client.session.get(url) as response:
                response.raise_for_status()

        except Exception:
            return -1.0

        return (perf_counter() - start_time) * 1000

    async def close(self):
        """ Close the underlying HTTP session used by the API client. This should be called when the API services are no longer needed to free up resources. """

        self._client.set_tokens(None, None)
        await self._client.close()
