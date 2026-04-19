import pytest
from unittest.mock import (
    patch,
    MagicMock,
    AsyncMock,
    PropertyMock,
)

from discord import (
    Embed,
)

from modules.Config import Config
from modules.Events.Events import Events, setup as setup_events
from modules.Events.Gossiper import Gossiper, setup as setup_gossiper
from modules.Events.Sync import Sync, setup as setup_sync
from modules.General import General

class TestModulesModule:
    @pytest.fixture
    def mock_lucy(self):
        """ Fixture that provides a mock Lucy instance with necessary attributes and methods for testing the modules. """

        lucy = MagicMock()
        lucy.latency = 0.05
        lucy.user.name = "LucyBot"
        lucy.user.display_avatar.url = "http://bot.com/avatar.png"
        lucy.OWNER.name = "Owner"
        lucy.OWNER.display_avatar.url = "http://owner.com/avatar.png"
        lucy.CONFIG = MagicMock()
        lucy.CONFIG.VERSION = "1.0.0"
        lucy.CONFIG.PRODUCTION = False
        lucy.CONFIG.TESTING_GUILD_ID = 123
        lucy.CONFIG.API_REST_USERNAME = "Lucy"
        lucy.CONFIG.API_REST_PASSWORD = "Lucy"
        lucy.cache = {
            "slash_cmds": {},
            "guilds": {
                "456": {"lang": {"code": "en"}},
            },
        }
        lucy.api = MagicMock()
        lucy.api.ping = AsyncMock(return_value=50.0)
        lucy.api._client.path = "http://api.test"
        lucy._cmd_err = AsyncMock()

        return lucy

    class TestConfig:
        @pytest.mark.asyncio
        async def test_lang_command_success(self, mock_lucy):
            """ Test that the lang command successfully updates the guild's language setting via the API and sends a confirmation message. """

            cog = Config(mock_lucy)
            interaction = AsyncMock()
            interaction.guild.id = 456
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            mock_lucy.api.guild.update = AsyncMock(return_value={"ok": True})
            
            await cog.lang.callback(cog, interaction, language="es")
            
            interaction.response.defer.assert_called_once()
            mock_lucy.api.guild.update.assert_called_with(interaction.guild.id, lang="es")
            interaction.followup.send.assert_called_once()
            _, kwargs = interaction.followup.send.call_args
            assert isinstance(kwargs["embed"], Embed)
            assert "✅" in kwargs["embed"].title

        @pytest.mark.asyncio
        async def test_lang_command_api_error(self, mock_lucy):
            """ Test that the lang command correctly handles API failures when attempting to update the guild's language and sends an error embed. """

            cog = Config(mock_lucy)
            interaction = AsyncMock()
            interaction.guild.id = 456
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            mock_lucy.api.guild.update = AsyncMock(side_effect=Exception("api error"))
            
            await cog.lang.callback(cog, interaction, language="es")
            
            _, kwargs = interaction.followup.send.call_args
            assert isinstance(kwargs["embed"], Embed)
            assert "⚠️" in kwargs["embed"].title

        @pytest.mark.asyncio
        async def test_lang_error_handler(self, mock_lucy):
            """ Test that the lang command's error handler correctly calls the bot's _cmd_err method with the expected arguments. """

            cog = Config(mock_lucy)
            interaction = AsyncMock()
            error = Exception("Test Error")
            
            await cog.lang_error(interaction, error)
            mock_lucy._cmd_err.assert_called_once_with("lang", interaction=interaction, error=error)

    class TestEvents:
        @pytest.mark.asyncio
        async def test_on_ready_logs(self, mock_lucy):
            """ Test that on_ready writes an informational log. """

            cog = Events(mock_lucy)

            with patch("modules.Events.Events.logger") as logger:
                await cog.on_ready()
                logger.info.assert_called_once_with("Events cog is ready. Listening for events.")

        @pytest.mark.asyncio
        async def test_on_guild_join_success(self, mock_lucy):
            """ Test that on_guild_join calls API when available. """

            cog = Events(mock_lucy)
            guild = MagicMock()
            guild.id = 123

            mock_lucy.api.guild.new = AsyncMock()

            await cog.on_guild_join(guild)

            mock_lucy.api.guild.new.assert_awaited_once_with(123)

        @pytest.mark.asyncio
        async def test_on_guild_join_no_api(self, mock_lucy):
            """ Test that on_guild_join exits when API is not available. """

            cog = Events(mock_lucy)
            mock_lucy.api = None
            guild = MagicMock()
            guild.id = 123

            await cog.on_guild_join(guild)

        @pytest.mark.asyncio
        async def test_on_guild_join_error_logs(self, mock_lucy):
            """ Test that on_guild_join logs failures. """

            cog = Events(mock_lucy)
            guild = MagicMock()
            guild.id = 123
            guild.name = "Guild"

            mock_lucy.api.guild.new = AsyncMock(side_effect=Exception("boom"))

            with patch("modules.Events.Events.logger") as logger:
                await cog.on_guild_join(guild)
                logger.error.assert_called_once()

        @pytest.mark.asyncio
        async def test_on_guild_remove_success(self, mock_lucy):
            """ Test that on_guild_remove calls API when available. """

            cog = Events(mock_lucy)
            guild = MagicMock()
            guild.id = 321

            mock_lucy.api.guild.delete = AsyncMock()

            await cog.on_guild_remove(guild)

            mock_lucy.api.guild.delete.assert_awaited_once_with(321)

        @pytest.mark.asyncio
        async def test_on_guild_remove_no_api(self, mock_lucy):
            """ Test that on_guild_remove exits when API is not available. """

            cog = Events(mock_lucy)
            mock_lucy.api = None
            guild = MagicMock()
            guild.id = 321

            await cog.on_guild_remove(guild)

        @pytest.mark.asyncio
        async def test_on_guild_remove_error_logs(self, mock_lucy):
            """ Test that on_guild_remove logs failures. """

            cog = Events(mock_lucy)
            guild = MagicMock()
            guild.id = 321
            guild.name = "Guild"

            mock_lucy.api.guild.delete = AsyncMock(side_effect=Exception("boom"))

            with patch("modules.Events.Events.logger") as logger:
                await cog.on_guild_remove(guild)
                logger.error.assert_called_once()

        @pytest.mark.asyncio
        async def test_setup_adds_cog(self, mock_lucy):
            """ Test that setup registers the Events cog in Lucy. """

            mock_lucy.add_cog = AsyncMock()

            await setup_events(mock_lucy)

            mock_lucy.add_cog.assert_awaited_once()
            added_cog = mock_lucy.add_cog.await_args.args[0]
            assert isinstance(added_cog, Events)

    class TestGossiper:
        @pytest.mark.asyncio
        async def test_on_ready_starts_listener(self, mock_lucy):
            """ Test that on_ready starts Redis listener and logs success. """

            cog = Gossiper(mock_lucy)

            with (
                patch.object(cog, "start_redis_listener", new_callable = AsyncMock) as start_listener,
                patch("modules.Events.Gossiper.logger") as logger,
            ):
                await cog.on_ready()
                start_listener.assert_awaited_once()
                logger.info.assert_called_once_with("Redis listener started successfully.")

        @pytest.mark.asyncio
        async def test_on_redis_message_dispatch_created(self, mock_lucy):
            """ Test that supported created events are dispatched to the corresponding handler. """

            cog = Gossiper(mock_lucy)
            payload = {"id": "999", "lang": {"code": "es"}}

            await cog.on_redis_message("lucy.guild.created", payload)

            assert mock_lucy.cache["guilds"]["999"] == payload

        @pytest.mark.asyncio
        async def test_on_redis_message_unsupported_logs_warning(self, mock_lucy):
            """ Test that unsupported Redis events are ignored with a warning. """

            cog = Gossiper(mock_lucy)

            with patch("modules.Events.Gossiper.logger") as logger:
                await cog.on_redis_message("lucy.user.updated", {"id": "1"})
                logger.warning.assert_called_once()

        @pytest.mark.asyncio
        async def test_on_redis_message_unhandled_logs_warning(self, mock_lucy):
            """ Test that events with no handler emit an unhandled warning. """

            cog = Gossiper(mock_lucy)
            cog._supported_models.add("token")
            cog._supported_events.add("rotated")

            with patch("modules.Events.Gossiper.logger") as logger:
                await cog.on_redis_message("lucy.token.rotated", {"id": "1"})
                logger.warning.assert_called_once()

        def test_on_redis_guild_deleted_removes_cache(self, mock_lucy):
            """ Test that guild deletion events remove guild from cache if present. """

            cog = Gossiper(mock_lucy)
            mock_lucy.cache["guilds"]["321"] = {"id": "321"}

            cog.on_redis_guild_deleted({"id": "321"})

            assert "321" not in mock_lucy.cache["guilds"]

        def test_cog_unload_skips_when_loop_closed(self, mock_lucy):
            """ Test that cog_unload exits quietly when event loop is already closed. """

            cog = Gossiper(mock_lucy)

            closed_loop = MagicMock()
            closed_loop.is_closed.return_value = True
            closed_loop.create_task = MagicMock()

            mock_lucy.loop = closed_loop

            with patch.object(type(cog._redis_bus), "is_running", new_callable = PropertyMock, return_value = True):
                cog.cog_unload()

            closed_loop.create_task.assert_not_called()

        @pytest.mark.asyncio
        async def test_setup_adds_cog(self, mock_lucy):
            """ Test that setup registers the Gossiper cog in Lucy. """

            mock_lucy.add_cog = AsyncMock()

            await setup_gossiper(mock_lucy)

            mock_lucy.add_cog.assert_awaited_once()
            added_cog = mock_lucy.add_cog.await_args.args[0]
            assert isinstance(added_cog, Gossiper)

    class TestSync:
        @pytest.mark.asyncio
        async def test_sync_api_success(self, mock_lucy):
            """ Test that sync_api initializes API services when endpoint is available. """

            cog = Sync(mock_lucy)

            with (
                patch("modules.Events.Sync.getenv", return_value = "http://api.test"),
                patch("modules.Events.Sync.ApiServices") as api_services_cls,
            ):
                api_instance = api_services_cls.return_value
                api_instance.ping = AsyncMock(return_value = 12.0)
                api_instance._client.path = "http://api.test"

                await cog.sync_api()

                assert mock_lucy.api == api_instance
                api_instance.ping.assert_awaited_once()
                assert api_instance._client.refresh_handler == cog._handle_api_auth_failure

        @pytest.mark.asyncio
        async def test_sync_api_fail_sets_api_none(self, mock_lucy):
            """ Test that sync_api closes client and resets api on ping failure. """

            cog = Sync(mock_lucy)

            with (
                patch("modules.Events.Sync.getenv", return_value = "http://api.test"),
                patch("modules.Events.Sync.ApiServices") as api_services_cls,
            ):
                api_instance = api_services_cls.return_value
                api_instance.ping = AsyncMock(return_value = -1)
                api_instance.close = AsyncMock()

                await cog.sync_api()

                assert mock_lucy.api is None
                api_instance.close.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_sync_commands_dev(self, mock_lucy):
            """ Test that sync_commands targets testing guild in development mode. """

            cog = Sync(mock_lucy)
            mock_lucy.CONFIG.PRODUCTION = False
            mock_lucy.CONFIG.TESTING_GUILD_ID = 123
            mock_lucy.tree.copy_global_to = MagicMock()
            mock_lucy.tree.sync = AsyncMock()

            with patch("modules.Events.Sync.Object") as Object:
                guild = Object.return_value

                await cog.sync_commands()

                mock_lucy.tree.copy_global_to.assert_called_once_with(guild = guild)
                mock_lucy.tree.sync.assert_awaited_once_with(guild = guild)

        @pytest.mark.asyncio
        async def test_sync_owner_sets_owner(self, mock_lucy):
            """ Test that sync_owner stores application owner on Lucy instance. """

            cog = Sync(mock_lucy)
            owner = MagicMock()
            mock_lucy.application_info = AsyncMock(return_value = MagicMock(owner = owner))

            await cog.sync_owner()

            assert mock_lucy.OWNER == owner

        @pytest.mark.asyncio
        async def test_sync_slash_cmds_cache_dev(self, mock_lucy):
            """ Test that sync_slash_cmds_cache updates cache and logs totals in dev mode. """

            cog = Sync(mock_lucy)
            mock_lucy.CONFIG.PRODUCTION = False
            mock_lucy.CONFIG.TESTING_GUILD_ID = 123

            cmd1 = MagicMock()
            cmd1.name = "help"
            cmd1.id = 1

            cmd2 = MagicMock()
            cmd2.name = "ping"
            cmd2.id = 2

            mock_lucy.tree.fetch_commands = AsyncMock(return_value = [cmd1, cmd2])

            with (
                patch("modules.Events.Sync.Object") as Object,
                patch("modules.Events.Sync.count_commands_in_files", return_value = 3),
                patch("modules.Events.Sync.logger") as logger,
            ):
                guild = Object.return_value

                await cog.sync_slash_cmds_cache()

                mock_lucy.tree.fetch_commands.assert_awaited_once_with(guild = guild)
                assert mock_lucy.cache["slash_cmds"] == {"help": 1, "ping": 2}
                logger.info.assert_called_once_with("Cached (2/3) commands.")

        @pytest.mark.asyncio
        async def test_sync_tokens_cache_no_api(self, mock_lucy):
            """ Test that sync_tokens_cache warns and exits if API is not initialized. """

            cog = Sync(mock_lucy)
            mock_lucy.api = None

            with patch("modules.Events.Sync.logger") as logger:
                await cog.sync_tokens_cache()
                logger.warning.assert_called_once_with("API not initialized. Cannot sync tokens.")

        @pytest.mark.asyncio
        async def test_handle_api_auth_failure_triggers_full_reauth(self, mock_lucy):
            """ Test that auth failure callback attempts full re-auth by calling sync_tokens_cache. """

            cog = Sync(mock_lucy)
            cog.sync_tokens_cache = AsyncMock()

            with patch("modules.Events.Sync.logger") as logger:
                await cog._handle_api_auth_failure()

                cog.sync_tokens_cache.assert_awaited_once()
                logger.warning.assert_called_once_with(
                    "API tokens expired and refresh failed. Attempting full re-authentication..."
                )

        @pytest.mark.asyncio
        async def test_handle_api_auth_failure_logs_critical_error(self, mock_lucy):
            """ Test that auth failure callback logs when re-auth attempt fails. """

            cog = Sync(mock_lucy)
            cog.sync_tokens_cache = AsyncMock(side_effect = Exception("boom"))

            with patch("modules.Events.Sync.logger") as logger:
                await cog._handle_api_auth_failure()

                logger.error.assert_called_once()

        @pytest.mark.asyncio
        async def test_setup_adds_cog(self, mock_lucy):
            """ Test that setup registers the Sync cog in Lucy. """

            mock_lucy.add_cog = AsyncMock()

            await setup_sync(mock_lucy)

            mock_lucy.add_cog.assert_awaited_once()
            added_cog = mock_lucy.add_cog.await_args.args[0]
            assert isinstance(added_cog, Sync)

    class TestGeneral:
        @pytest.mark.asyncio
        async def test_ping_command(self, mock_lucy):
            """ Test that the ping command returns the correct latency information. """

            cog = General(mock_lucy)
            interaction = AsyncMock()
            interaction.guild.id = 456
            interaction.client.latency = 0.05
            
            await cog.ping.callback(cog, interaction)
            
            interaction.response.send_message.assert_called_once()
            _, kwargs = interaction.response.send_message.call_args
            assert isinstance(kwargs["embed"], Embed)
            
            found_latency = False
            for field in kwargs["embed"].fields:
                if "50ms" in field.value:
                    found_latency = True
            assert found_latency

        @pytest.mark.asyncio
        async def test_help_command_no_category(self, mock_lucy):
            """ Test that the help command without a category sends a general help embed with the correct information. """

            cog = General(mock_lucy)
            interaction = AsyncMock()
            interaction.guild.id = 456
            interaction.followup.send = AsyncMock()
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            
            bot_info = {
                "bot_name": "Lucy",
                "bot_avatar_url": "http://bot.com/avatar.png",
                "owner_name": "Owner",
                "owner_avatar_url": "http://owner.com/avatar.png",
                "version": "1.0.0",
                "slash_cmds_cache": {}
            }
            
            with (
                patch("modules.General.get_cogs_dict", return_value={}),
                patch("modules.General.get_bot_info", return_value=bot_info),
                patch("modules.General.GeneralHelpView"),
                patch("modules.General.general_help_embed")
            ):
                
                await cog.help.callback(cog, interaction)
                
                interaction.response.defer.assert_called_once()
                interaction.followup.send.assert_called_once()

        @pytest.mark.asyncio
        async def test_help_command_with_category(self, mock_lucy):
            """ Test that the help command with a specific category retrieves the appropriate assistance information and sends the corresponding embed. """

            cog = General(mock_lucy)
            interaction = AsyncMock()
            interaction.guild.id = 456
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "es"})
            cogs_dict = {"General": {"name": "general", "app_commands": []}}
            
            with (
                patch("modules.General.get_cogs_dict", return_value=cogs_dict),
                patch("modules.General.get_bot_info", return_value={}),
                patch("modules.General.cog_help_embed") as mock_embed,
                patch("modules.General.GeneralHelpView")
            ):
                
                await cog.help.callback(cog, interaction, category="General")
                
                mock_embed.assert_called_once()
                interaction.followup.send.assert_called_once()

        @pytest.mark.asyncio
        async def test_help_command_invalid_category(self, mock_lucy):
            """ Test that the help command sends a descriptive warning when an invalid or non-existent category is provided. """

            cog = General(mock_lucy)
            interaction = AsyncMock()
            interaction.guild.id = 456
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            
            with patch("modules.General.get_cogs_dict", return_value={}):
                await cog.help.callback(cog, interaction, category="Inexistente")
                
                interaction.followup.send.assert_called_with(
                    "Category 'Inexistente' not found.", 
                    ephemeral=True
                )
