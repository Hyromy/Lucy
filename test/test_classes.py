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
from classes.Config import (
    Config,
    ConfigErr,
)
from classes.Lucy import(
    Lucy,
)
from classes.RedisEventBus import (
    RedisEventBus,
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

        def test_set_tokens_sets_values(self):
            """ Test that set_tokens stores tokens and expiration timestamp from JWT payload. """

            api = _ApiClient("http://example.com")

            with patch("classes.Api.jwt_decode", return_value = {"exp": 1234567890}):
                api.set_tokens("access", "refresh")

            assert api._token == "access"
            assert api._refreshing_token == "refresh"
            assert api._expire_at == 1234567890

        def test_set_tokens_on_decode_error(self):
            """ Test that set_tokens falls back to exp=0 when token decoding fails. """

            api = _ApiClient("http://example.com")

            with patch("classes.Api.jwt_decode", side_effect = Exception("invalid token")):
                api.set_tokens("access", "refresh")

            assert api._token == "access"
            assert api._refreshing_token == "refresh"
            assert api._expire_at == 0

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

        @pytest.mark.asyncio
        async def test_request_adds_auth_header(self):
            """ Test that authenticated requests include a Bearer Authorization header. """

            session = MagicMock()
            session.closed = False

            response = MagicMock()
            response.raise_for_status.return_value = None
            response.json = AsyncMock(return_value = {"ok": True})

            context_manager = MagicMock()
            context_manager.__aenter__ = AsyncMock(return_value = response)
            context_manager.__aexit__ = AsyncMock(return_value = None)
            session.request.return_value = context_manager

            api = _ApiClient("http://example.com", session = session)
            api._token = "abc123"
            api._expire_at = 9999999999

            result = await api.get("guild")

            assert result == {"ok": True}
            _, kwargs = session.request.call_args
            assert kwargs["headers"]["Authorization"] == "Bearer abc123"

        @pytest.mark.asyncio
        async def test_request_refreshes_token_when_expiring(self):
            """ Test that refresh_handler is awaited when access token is close to expiration. """

            session = MagicMock()
            session.closed = False

            response = MagicMock()
            response.raise_for_status.return_value = None
            response.json = AsyncMock(return_value = {"ok": True})

            context_manager = MagicMock()
            context_manager.__aenter__ = AsyncMock(return_value = response)
            context_manager.__aexit__ = AsyncMock(return_value = None)
            session.request.return_value = context_manager

            api = _ApiClient("http://example.com", session = session)
            api._token = "abc123"
            api._expire_at = 0
            api.refresh_handler = AsyncMock()

            await api.get("guild")

            api.refresh_handler.assert_awaited_once()

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
            assert guild.endpoint == "api/guilds"
            assert guild.url == url + "api/guilds/"

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

        @pytest.mark.asyncio
        async def test_ping(self):
            """ Test that the ping method correctly measures latency and handles errors. """

            url = "http://example.com/api/"
            session = MagicMock()
            session.closed = False

            api_services = ApiServices(url, session = session)

            # Test successful ping
            response = MagicMock()
            response.status = 200

            context_manager = MagicMock()
            context_manager.__aenter__ = AsyncMock(return_value = response)
            context_manager.__aexit__ = AsyncMock(return_value = None)

            session.get.return_value = context_manager

            latency = await api_services.ping()
            assert latency >= 0
            session.get.assert_called_once_with(f"{url}api/health/")

            # Test ping with connection error
            session.get.reset_mock()
            session.get.side_effect = ClientConnectionError()

            latency = await api_services.ping()
            assert latency == -1.0
            session.get.assert_called_once_with(f"{url}api/health/")

        @pytest.mark.asyncio
        async def test_close(self):
            """ Test that the close method correctly closes the underlying API client session. """
        
            url = "http://example.com/api/"
            session = AsyncMock()
            session.closed = False
            api_services = ApiServices(url, session = session)
        
            await api_services.close()
            session.close.assert_awaited_once()

class TestConfigModule:
    class TestConfig:
        def test_instance(self):
            """ Test that a Config instance is created correctly with the expected properties. """

            env_vars = {
                "PRODUCTION": "False",
                "TESTING_DISCORD_BOT_TOKEN": "abc",
                "TESTING_GUILD_ID": "123"
            }
            with patch("classes.Config.load_dotenv"), patch.dict("os.environ", env_vars, clear = True):
                config = Config()

                assert config is not None
                assert config.PREFIX == ","
                assert config.TOKEN == "abc"
                assert config.TESTING_GUILD_ID == "123"
                assert not config.PRODUCTION

        def test_missing_token_prod(self):
            """ Test that a ConfigErr is raised if the required token is missing in production. """

            with patch("classes.Config.load_dotenv"), patch.dict("os.environ", {"PRODUCTION": "True"}, clear = True):
                with pytest.raises(ConfigErr) as exc:
                    Config()
                assert "DISCORD_BOT_TOKEN" in str(exc.value)

        def test_missing_token_dev(self):
            """ Test that ConfigErr is raised if variables are missing in dev. """
            
            # Missing TOKEN
            with patch("classes.Config.load_dotenv"), patch.dict("os.environ", {"PRODUCTION": "False"}, clear = True):
                with pytest.raises(ConfigErr) as exc:
                    Config()
                assert "TESTING_DISCORD_BOT_TOKEN" in str(exc.value)

            # Missing GUILD_ID
            env_only_token = {"PRODUCTION": "False", "TESTING_DISCORD_BOT_TOKEN": "abc"}
            with patch("classes.Config.load_dotenv"), patch.dict("os.environ", env_only_token, clear = True):
                with pytest.raises(ConfigErr) as exc:
                    Config()
                assert "TESTING_GUILD_ID" in str(exc.value)

class TestLucyModule:
    class TestLucy:
        def test_instance(self):
            """ Test that a Lucy instance is created correctly with the expected default properties and methods. """

            mock_config = MagicMock(spec=Config)
            mock_config.PREFIX = "!"
            mock_config.PRODUCTION = False
            mock_config.TESTING_GUILD_ID = "123"

            lucy = Lucy(config=mock_config)

            assert lucy.command_prefix == "!"
            assert lucy.intents == Intents.default()
            assert lucy.CONFIG == mock_config
            assert lucy.get_command("help") is not None

        @pytest.mark.asyncio
        async def test_load_cogs(self):
            """ Test that the _load_cogs method correctly loads valid cog files. """

            lucy = Lucy(config=MagicMock())

            with (
                patch("classes.Lucy.os.walk") as walk,
                patch("classes.Lucy.logger"),
                patch.object(lucy, "load_extension", new_callable=AsyncMock) as load_extension,
            ):
                walk.return_value = [
                    ("modules", [], ["MyCog.py", "anotherCog.py", "__init__.py", "notACog.txt"]),
                    ("cogs", [], ["MayBeACog.txt", "_Cog.py", "1Invalid.py", "Valid_Cog.py"]),
                    ("modules/Events", [], ["Events.py"]),
                ]
                load_extension.return_value = None

                await lucy._load_cogs("cogs")

                walk.assert_called_once_with("cogs")
                load_extension.assert_any_await("cogs.Valid_Cog")
                assert load_extension.await_count == 3

        @pytest.mark.asyncio
        async def test_load_cogs_on_err(self):
            """ Test that the _load_cogs method logs errors when loading raise exceptions. """

            lucy = Lucy(config=MagicMock())

            with (
                patch("classes.Lucy.os.walk") as walk,
                patch("classes.Lucy.logger") as logger,
                patch.object(lucy, "load_extension", new_callable = AsyncMock) as load_extension,
            ):
                walk.return_value = [
                    ("cogs", [], ["InvalidCog.py"])
                ]

                load_extension.side_effect = Exception("Failed to load cog")

                await lucy._load_cogs("cogs")

                walk.assert_called_once_with("cogs")
                load_extension.assert_awaited_once_with("cogs.InvalidCog")
                logger.error.assert_called_once()
                assert len(lucy.cogs) == 0

        @pytest.mark.asyncio
        async def test_cmd_err(self):
            """ Test that the _cmd_err method logs the error and sends an appropriate response to the user. """

            lucy = Lucy(config=MagicMock())

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
            
            lucy = Lucy(config=MagicMock())

            with patch.object(lucy, "_load_cogs", new_callable = AsyncMock) as mock_load_cogs:
                await lucy.setup()

                mock_load_cogs.assert_awaited_once()
                assert lucy.get_command("help") is None

        @pytest.mark.asyncio
        async def test_start(self):
            """ Test that the start method calls the parent start method with the provided token. """
            
            lucy = Lucy(config=MagicMock())

            with patch.object(Bot, "start", new_callable = AsyncMock) as mock_super_start:
                await lucy.start("fake_token")
                mock_super_start.assert_awaited_once_with("fake_token")

        @pytest.mark.asyncio
        async def test_close(self):
            """ Test that the close method calls the parent close method and closes the API client if it exists. """
            
            lucy = Lucy(config = MagicMock(), apiServices = AsyncMock())

            with patch.object(Bot, "close", new_callable = AsyncMock) as mock_super_close:
                await lucy.close()
                mock_super_close.assert_awaited_once()
                lucy.api.close.assert_awaited_once()


class TestRedisEventBusModule:
    class TestRedisEventBus:
        @pytest.mark.asyncio
        async def test_start_without_redis_url(self):
            """ Test that start returns False and logs warning if REDIS_URL is missing. """

            with (
                patch("classes.RedisEventBus.getenv", return_value = None),
                patch("classes.RedisEventBus.logger") as logger,
            ):
                bus = RedisEventBus()
                result = await bus.start(on_event = AsyncMock())

                assert result is False
                logger.warning.assert_called_once_with("REDIS_URL not found in env; Redis event listener disabled.")

        @pytest.mark.asyncio
        async def test_start_when_already_running(self):
            """ Test that start exits early when listener task already exists. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")
            bus._task = object()

            with patch("classes.RedisEventBus.redis.from_url") as from_url:
                result = await bus.start(on_event = AsyncMock())

                assert result is True
                from_url.assert_not_called()

        @pytest.mark.asyncio
        async def test_start_success(self):
            """ Test that start initializes redis pubsub, subscribes and creates listener task. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")

            redis_client = MagicMock()
            pubsub = MagicMock()
            pubsub.psubscribe = AsyncMock()
            redis_client.pubsub.return_value = pubsub

            fake_task = object()

            def _create_task(coro):
                coro.close()
                return fake_task

            with (
                patch("classes.RedisEventBus.redis.from_url", return_value = redis_client),
                patch("classes.RedisEventBus.create_task", side_effect = _create_task),
            ):
                result = await bus.start(on_event = AsyncMock())

                assert result is True
                pubsub.psubscribe.assert_awaited_once_with("lucy.*")
                assert bus._task is fake_task

        @pytest.mark.asyncio
        async def test_stop_cancels_task_and_closes_clients(self):
            """ Test that stop cancels running task and closes clients. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")

            loop = __import__("asyncio").get_running_loop()
            task = loop.create_future()
            task.set_result(None)
            bus._task = task

            bus._close_clients = AsyncMock()

            await bus.stop()

            assert bus._task is None
            bus._close_clients.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_close_clients(self):
            """ Test that _close_clients closes pubsub and redis client and clears references. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")
            bus._pubsub = MagicMock()
            bus._pubsub.close = AsyncMock()
            bus._redis = MagicMock()
            bus._redis.aclose = AsyncMock()

            pubsub = bus._pubsub
            redis_client = bus._redis

            await bus._close_clients()

            pubsub.close.assert_awaited_once()
            redis_client.aclose.assert_awaited_once()
            assert bus._pubsub is None
            assert bus._redis is None

        @pytest.mark.asyncio
        async def test_listener_loop_dispatches_valid_event(self):
            """ Test that _listener_loop decodes and dispatches valid pmessage payloads. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")

            async def _messages():
                yield {
                    "type": "pmessage",
                    "channel": b"lucy.guild.updated",
                    "data": b'{"id":"1","event":"lucy.guild.updated"}',
                }

            pubsub = MagicMock()
            pubsub.listen = _messages
            bus._pubsub = pubsub

            on_event = AsyncMock()

            await bus._listener_loop(on_event = on_event)

            on_event.assert_awaited_once_with(
                "lucy.guild.updated",
                {"id": "1", "event": "lucy.guild.updated"},
            )

        @pytest.mark.asyncio
        async def test_listener_loop_invalid_json(self):
            """ Test that _listener_loop ignores invalid JSON payloads. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")

            async def _messages():
                yield {
                    "type": "pmessage",
                    "channel": "lucy.guild.updated",
                    "data": "not-json",
                }

            pubsub = MagicMock()
            pubsub.listen = _messages
            bus._pubsub = pubsub

            on_event = AsyncMock()

            with patch("classes.RedisEventBus.logger") as logger:
                await bus._listener_loop(on_event = on_event)
                logger.warning.assert_called_once()

            on_event.assert_not_awaited()

        @pytest.mark.asyncio
        async def test_listener_loop_json_not_object(self):
            """ Test that _listener_loop ignores JSON payloads that are not objects. """

            bus = RedisEventBus(redis_url = "redis://localhost:6379")

            async def _messages():
                yield {
                    "type": "pmessage",
                    "channel": "lucy.guild.updated",
                    "data": "[1, 2, 3]",
                }

            pubsub = MagicMock()
            pubsub.listen = _messages
            bus._pubsub = pubsub

            on_event = AsyncMock()

            with patch("classes.RedisEventBus.logger") as logger:
                await bus._listener_loop(on_event = on_event)
                logger.warning.assert_called_once()

            on_event.assert_not_awaited()
