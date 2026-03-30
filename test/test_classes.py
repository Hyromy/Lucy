import pytest
from unittest.mock import (
    patch,
    MagicMock,
    AsyncMock,
)

from discord import (
    Intents,
)
from discord.ext.commands import (
    Bot,
)

from classes.Api import (
    ClientResponseError,
    ClientConnectionError,

    _ApiClient,
    _ApiInterface,

    _Guild,

    ApiServices,
)
from classes.Lucy import(
    Lucy,
)

class TestApiModule:
    class TestApiClient:
        def test_instance(self):
            """ Test that an _ApiClient instance is created correctly. """

            path = "http://example.com/"
            api = _ApiClient(path)

            assert api is not None
            assert api.path == path
            assert api._session is None

        def test_session(self):
            """ Test that the session property creates a new session if one does not exist, and returns the existing session if it does. """

            # without a session provided, it should create one
            with patch("classes.Api.ClientSession") as session:
                session: MagicMock

                api = _ApiClient("http://example.com")

                assert api._session is None
                assert api.session == session.return_value
                assert api._session == session.return_value

            # with a session provided, it should use that one
            session = MagicMock()
            session.closed = False

            api = _ApiClient("http://example.com", session = session)

            assert api._session == session
            assert api.session == session

        @pytest.mark.asyncio
        async def test_session_closed(self):
            """ Test that if the session is closed, a new one is created on next access. """

            # close an existing session and ensure it creates a new one on next access
            session = AsyncMock()
            session.closed = False

            api = _ApiClient("http://example.com", session = session)
            await api.close()

            session.close.assert_awaited_once()
            assert api._session is None

            # close an already closed session and ensure it does not raise an error
            api2 = _ApiClient("http://example.com")
            await api2.close()
            assert api2._session is None

        def test_is_retryable(self):
            """ Test that the _is_retryable method correctly identifies retryable exceptions and responses. """

            assert _ApiClient._is_retryable(ClientConnectionError())
            assert _ApiClient._is_retryable(TimeoutError())
            assert _ApiClient._is_retryable(
                ClientResponseError(None, None, status = 502)
            )
            assert not _ApiClient._is_retryable(
                ClientResponseError(None, None, status = 400)
            )
            assert not _ApiClient._is_retryable(ValueError())

        @pytest.mark.asyncio
        async def test_retry(self):
            """ Test that the retry mechanism works correctly for retryable errors and responses. """

            session = MagicMock()
            session.closed = False
            response_data = {"success": True}

            r_502 = MagicMock()
            r_502.status = 502
            r_502.raise_for_status.side_effect = ClientResponseError(None, None, status = 502)

            r_200 = MagicMock()
            r_200.status = 200
            r_200.json = AsyncMock(return_value = response_data)
            r_200.raise_for_status.return_value = None

            ctx_manager = MagicMock()
            ctx_manager.__aenter__ = AsyncMock(side_effect = [r_502, r_200])
            ctx_manager.__aexit__ = AsyncMock(return_value = None)

            session.request.return_value = ctx_manager

            api = _ApiClient("http://example.com", session = session)

            assert await api.get("test") == response_data
            assert session.request.call_count == 2

        @pytest.mark.asyncio
        async def test_retry_on_400(self):
            """ Test that the retry mechanism does not retry on non-retryable errors (e.g. 400 Bad Request). """

            session = MagicMock()
            session.closed = False

            r_404 = MagicMock(status = 400)
            r_404.raise_for_status.side_effect = ClientResponseError(None, None, status = 400)

            ctx_manager = MagicMock()
            ctx_manager.__aenter__ = AsyncMock(return_value = r_404)
            session.request.return_value = ctx_manager

            api = _ApiClient("http://example.com", session = session)

            with pytest.raises(ClientResponseError) as exc:
                await api.get("test")

            assert exc.value.status == 400
            assert session.request.call_count == 1

        @pytest.mark.asyncio
        async def test_retry_on_net_err(self):
            """ Test that the retry mechanism retries on network errors (e.g. ClientConnectionError) and succeeds on a subsequent attempt. """

            response_data = {"success": True}
            session = MagicMock()
            session.closed = False

            success_response = MagicMock()
            success_response.raise_for_status.return_value = None
            success_response.json = AsyncMock(return_value = response_data)

            ctx_manager = MagicMock()
            ctx_manager.__aenter__ = AsyncMock(
                side_effect = [ClientConnectionError(), success_response]
            )
            ctx_manager.__aexit__ = AsyncMock(return_value = None)

            session.request.return_value = ctx_manager

            api = _ApiClient("http://example.com", session = session)

            assert await api.get("test") == response_data
            assert session.request.call_count == 2

        @pytest.mark.asyncio
        async def test_retry_on_unexpected_err(self):
            """ Test that the retry mechanism does not retry on unexpected errors (e.g. ValueError) and raises the error immediately. """

            session = MagicMock()
            session.closed = False

            context_manager = MagicMock()
            context_manager.__aenter__ = AsyncMock(side_effect = ValueError("Unexpected error"))

            session.request.return_value = context_manager

            api = _ApiClient("http://example.com", session = session)

            with pytest.raises(ValueError):
                await api.get("test")

            assert session.request.call_count == 1

        @pytest.mark.asyncio
        async def test_retry_on_timeout(self):
            """ Test that the retry mechanism retries on TimeoutError and succeeds on a subsequent attempt. """

            session = MagicMock()
            session.closed = False

            response = MagicMock()
            response.raise_for_status.return_value = None
            response.json = AsyncMock(return_value = {})

            context_manager = MagicMock()
            context_manager.__aenter__ = AsyncMock(return_value = response)

            session.request.return_value = context_manager

            api = _ApiClient("http://example.com", session = session)

            await api.get("test")

            _, kwargs = session.request.call_args
            assert kwargs["timeout"] == api._timeout

    class TestApiInterface:
        def test_instance(self):
            """ Test that an _ApiInterface subclass can be created correctly and has the expected properties and methods. """

            class DummyApiService(_ApiInterface):
                def __init__(self, client: _ApiClient, endpoint: str):
                    super().__init__(client, endpoint)

                def new(self):
                    pass

            path = "http://example.com/"
            endpoint = "dummy/"

            client = _ApiClient(path)
            service = DummyApiService(client, endpoint)

            assert service is not None
            assert service.client == client
            assert service.endpoint == endpoint
            assert service.url == path + endpoint
            
            assert hasattr(service, "get")
            assert hasattr(service, "new")
    
    class TestGuild:
        def test_instance(self):
            """ Test that a _Guild instance is created correctly with the correct endpoint and URL. """

            url = "http://example.com/api/"
            guild = _Guild(_ApiClient(url))

            assert guild is not None
            assert guild.endpoint == "guild"
            assert guild.url == url + "guild/"

    class TestApiServices:
        def test_instance(self):
            """ Test that an ApiServices instance is created correctly with the correct path and session. """

            url = "http://example.com/api/"
            session = MagicMock()
            api_services = ApiServices(url, session = session)

            assert api_services is not None 

            services = [
                ("guild", _Guild),
            ]

            assert all(
                isinstance(getattr(api_services, name), cls)
                for name, cls in services
            )

class TestLucyModule:
    class TestLucy:
        def test_instance(self):
            """ Test that a Lucy instance is created correctly with the expected default properties and methods. """

            lucy = Lucy()

            assert lucy.command_prefix == "!"
            assert lucy.intents == Intents.default()
            assert lucy.PRODUCTION == False
            assert lucy.get_command("help") is not None

        @pytest.mark.asyncio
        async def test_load_cogs(self):
            """ Test that the _load_cogs method correctly loads valid cog files. """

            lucy = Lucy()

            with (
                patch("classes.Lucy.listdir") as listdir,
                patch("classes.Lucy.logger"),
                patch.object(lucy, "load_extension", new_callable=AsyncMock) as load_extension,
            ):
                listdir.return_value = [
                    "MyCog.py",
                    "anotherCog.py",
                    "__init__.py",
                    "notACog.txt",
                    "MayBeACog.txt",
                    "_Cog.py",
                    "1Invalid.py",
                    "Valid_Cog.py",
                ]
                load_extension.return_value = None

                await lucy._load_cogs("cogs")

                listdir.assert_called_once_with("cogs")
                load_extension.assert_any_await("cogs.MyCog")
                load_extension.assert_any_await("cogs.Valid_Cog")
                assert load_extension.await_count == 2

        @pytest.mark.asyncio
        async def test_load_cogs_on_err(self):
            """ Test that the _load_cogs method logs errors when loading raise exceptions. """

            lucy = Lucy()

            with (
                patch("classes.Lucy.listdir") as listdir,
                patch("classes.Lucy.logger") as logger,
                patch.object(lucy, "load_extension", new_callable = AsyncMock) as load_extension,
            ):
                listdir.return_value = ["InvalidCog.py"]
                load_extension.side_effect = Exception("Failed to load cog")

                await lucy._load_cogs("cogs")

                listdir.assert_called_once_with("cogs")
                load_extension.assert_awaited_once_with("cogs.InvalidCog")
                logger.error.assert_called_once()
                assert len(lucy.cogs) == 0

        @pytest.mark.asyncio
        async def test_cmd_err(self):
            """ Test that the _cmd_err method logs the error and sends an appropriate response to the user. """

            lucy = Lucy()

            interaction = MagicMock()
            interaction.response.is_done.return_value = False
            interaction.response.send_message = AsyncMock()
            interaction.followup.send = AsyncMock()

            error = Exception("Test command error")

            with patch("classes.Lucy.logger") as mock_logger:
                await lucy._cmd_err("test", interaction = interaction, error = error)

                mock_logger.error.assert_called_once_with(
                    "Error in test command",
                    exc_info = error
                )
                interaction.response.send_message.assert_awaited_once_with(
                    "An error occurred while processing the command.",
                    ephemeral = True
                )
                interaction.followup.send.assert_not_awaited()

        @pytest.mark.asyncio
        async def test_setup(self):
            """ Test that the setup method removes the default help command and loads cogs. """
            
            lucy = Lucy()

            with patch.object(lucy, "_load_cogs", new_callable = AsyncMock) as mock_load_cogs:
                await lucy.setup()

                mock_load_cogs.assert_awaited_once()
                assert lucy.get_command("help") is None

        @pytest.mark.asyncio
        async def test_start(self):
            """ Test that the start method calls the parent start method with the provided token. """
            
            lucy = Lucy()

            with patch.object(Bot, "start", new_callable = AsyncMock) as mock_super_start:
                await lucy.start("fake_token")
                mock_super_start.assert_awaited_once_with("fake_token")

        @pytest.mark.asyncio
        async def test_close(self):
            """ Test that the close method calls the parent close method and closes the API client if it exists. """
            
            lucy = Lucy(apiServices = AsyncMock())

            with patch.object(Bot, "close", new_callable = AsyncMock) as mock_super_close:
                await lucy.close()
                mock_super_close.assert_awaited_once()
                lucy.api.close.assert_awaited_once()
