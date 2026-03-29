from aiohttp import ClientSession

from decorators import validations

class Api:
    def __init__(self, rest_url: str, test_endpoint: str = "api/"):
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
