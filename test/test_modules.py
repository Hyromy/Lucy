import pytest
from unittest.mock import (
    patch,
    MagicMock,
    AsyncMock,
)

from discord import (
    Embed,
    Object,
)

from modules.Config import Config
from modules.Events import Events
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
        lucy.VERSION = "1.0.0"
        lucy.PRODUCTION = False
        lucy.TESTING_GUILD_ID = 123
        lucy.cache = {"slash_cmds": {}}
        lucy.api = MagicMock()
        lucy._cmd_err = AsyncMock()

        return lucy

    class TestConfig:
        @pytest.mark.asyncio
        async def test_lang_command_success(self, mock_lucy):
            """ Test that the lang command successfully updates the guild's language setting via the API and sends a confirmation message. """

            cog = Config(mock_lucy)
            interaction = AsyncMock()
            interaction.guild_id = 456
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            mock_lucy.api.guild.patch = AsyncMock(return_value={"ok": True})
            
            await cog.lang.callback(cog, interaction, language="es")
            
            interaction.response.defer.assert_called_once()
            mock_lucy.api.guild.patch.assert_called_with(interaction.guild.id, lang="es")
            interaction.followup.send.assert_called_once()
            _, kwargs = interaction.followup.send.call_args
            assert isinstance(kwargs["embed"], Embed)
            assert "✅" in kwargs["embed"].title

        @pytest.mark.asyncio
        async def test_lang_command_api_error(self, mock_lucy):
            """ Test that the lang command correctly handles API failures when attempting to update the guild's language and sends an error embed. """

            cog = Config(mock_lucy)
            interaction = AsyncMock()
            interaction.guild_id = 456
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            mock_lucy.api.guild.patch = AsyncMock(return_value={"ok": False})
            
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
        async def test_sync_api_success(self, mock_lucy):
            """ Test that the sync_api method successfully initializes the API client and assigns it to the Lucy instance when the API is available. """

            cog = Events(mock_lucy)
            mock_lucy.api = None
            
            with (
                patch("modules.Events.getenv", return_value="http://api.test"),
                patch("modules.Events.ApiServices") as mock_api_class
            ):
                
                mock_api_instance = mock_api_class.return_value
                mock_api_instance.test = AsyncMock(return_value={"status": "ok"})
                
                await cog.sync_api()
                
                assert mock_lucy.api is not None
                mock_api_instance.test.assert_called_once()

        @pytest.mark.asyncio
        async def test_sync_api_fail(self, mock_lucy):
            """ Test that the sync_api method handles failures properly by closing the session and setting the api instance to None if the initialization test fails. """

            cog = Events(mock_lucy)
            mock_lucy.api = MagicMock()
            
            with (
                patch("modules.Events.getenv", return_value="http://api.test"),
                patch("modules.Events.ApiServices") as mock_api_class
            ):
                mock_api_instance = mock_api_class.return_value
                mock_api_instance.test = AsyncMock(return_value={"status": "error"})
                mock_api_instance.close = AsyncMock()
                
                await cog.sync_api()
                
                assert mock_lucy.api is None
                mock_api_instance.close.assert_called_once()

        @pytest.mark.asyncio
        async def test_sync_owner(self, mock_lucy):
            """ Test that the sync_owner method retrieves the application info and updates the OWNER attribute of the Lucy instance with the correct owner information. """

            cog = Events(mock_lucy)
            mock_lucy.application_info = AsyncMock()
            mock_owner = MagicMock()
            mock_owner.name = "RealOwner"
            mock_lucy.application_info.return_value.owner = mock_owner
            
            await cog.sync_owner()
            
            assert mock_lucy.OWNER.name == "RealOwner"

        @pytest.mark.asyncio
        async def test_sync_commands_dev(self, mock_lucy):
            """ Test that the sync_commands method correctly attempts to sync commands to the testing guild when the bot is not in production mode. """

            cog = Events(mock_lucy)
            mock_lucy.PRODUCTION = False
            mock_lucy.TESTING_GUILD_ID = 987
            mock_lucy.tree.sync = AsyncMock()
            
            with patch("modules.Events.Object") as mock_obj:
                await cog.sync_commands()
                mock_obj.assert_called_with(987)
                mock_lucy.tree.sync.assert_called_once()

    class TestGeneral:
        @pytest.mark.asyncio
        async def test_ping_command(self, mock_lucy):
            """ Test that the ping command returns the correct latency information. """

            cog = General(mock_lucy)
            interaction = AsyncMock()
            
            await cog.ping.callback(cog, interaction)
            
            interaction.response.send_message.assert_called_once()
            response_text = interaction.response.send_message.call_args[0][0]
            assert "Pong!" in response_text
            assert "50.00ms" in response_text

        @pytest.mark.asyncio
        async def test_help_command_no_category(self, mock_lucy):
            """ Test that the help command without a category sends a general help embed with the correct information. """

            cog = General(mock_lucy)
            interaction = AsyncMock()
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
            
            mock_lucy.api.guild.get = AsyncMock(return_value={"lang": "en"})
            
            with patch("modules.General.get_cogs_dict", return_value={}):
                await cog.help.callback(cog, interaction, category="Inexistente")
                
                interaction.followup.send.assert_called_with(
                    "Category 'Inexistente' not found.", 
                    ephemeral=True
                )
