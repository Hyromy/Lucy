from aiohttp import ClientSession

from decorators.patterns import singleton
from decorators import validations

@singleton
class Api:
    def __init__(self, rest_url: str, test_endpoint: str = ""):
        if not rest_url:
            raise ValueError("REST URL must be provided for Api instance.")

        self.__session: ClientSession = None
        self.__url = rest_url.rstrip("/")
        self.__test_endpoint = test_endpoint
        
        try:
            self.connect()
        except Exception as e:
            raise ConnectionError(f"Client session could not be established: {e}") from e

        self.guild = self.__Guild(self)

    def connect(self):
        self.__session = ClientSession()

    async def close(self):
        if self.__session:
            await self.__session.close()
            self.__session = None

    async def test(self):
        return await self._request("GET", self.__test_endpoint)

    async def _request(self, method: str, endpoint: str, /, **kwargs):
        async with self.__session.request(
            method,
            f"{self.__url}/{endpoint}",
            **kwargs
        ) as response:
            response.raise_for_status()
            return await response.json()

    class __Guild:
        def __init__(self, parent):
            self.__parent: Api = parent
            self.__endpoint = "guild/"

        @validations.args_required([("id", str)])
        async def get(self, id: str):
            return await self.__parent._request("GET", f"{self.__endpoint}{id}")
        
        @validations.args_required([("name", str)])
        async def post(self, name: str):
            return await self.__parent._request("POST", self.__endpoint, json = {
                "name": name
            })
        
        @validations.args_required([("id", str)])
        async def patch(self, id: str, /, *, 
            name: str = None,
            lang: str = None
        ):
            return await self.__parent._request("PATCH", f"{self.__endpoint}{id}", json = {
                "name": name,
                "lang": lang
            })
        
        @validations.args_required([("id", str)])
        async def delete(self, id: str):
            return await self.__parent._request("DELETE", f"{self.__endpoint}{id}")
