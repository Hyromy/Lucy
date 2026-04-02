import pytest
from unittest.mock import (
    MagicMock,
    AsyncMock,
)

from discord import (
    Embed,
)

from decorators.validations import (
    args_required,
    api_required,
    restrict_to_author,
)

class TestDecoratorsModule:
    class TestValidations:
        class TestArgsRequired:
            def test_all_pass(self):
                """ Test that args_required passes when all arguments are provided and valid. """

                @args_required()
                def func(a, b):
                    return a + b

                assert func(1, 2) == 3

            def test_falsy_fail(self):
                """ Test that args_required raises ValueError when an argument is None or falsy. """

                @args_required()
                def func(a, b):
                    return a + b
                
                with pytest.raises(ValueError, match="must not be None or falsy"):
                    func(None, 2)

            def test_specific_type(self):
                """ Test that args_required raises ValueError when an argument type is incorrect. """
                
                @args_required([("a", int)])
                def func(a):
                    return a
                
                with pytest.raises(ValueError, match="must be of type int"):
                    func("not an int")

            @pytest.mark.asyncio
            async def test_async_function(self):
                """ Test that args_required works correctly with async functions. """

                @args_required()
                async def func(a):
                    return a

                assert await func(1) == 1

            def test_empty_string_fail(self):
                """ Test that args_required fails with strings that are only whitespace. """

                @args_required([("a", str)])
                def func(a):
                    return a

                with pytest.raises(ValueError, match="non-empty string"):
                    func("   ")

        class TestApiRequired:
            @pytest.mark.asyncio
            async def test_available(self):
                """ Test that api_required allows execution if the API is available. """
                
                class Dummy:
                    def __init__(self):
                        self.lucy = MagicMock()
                        self.lucy.api = MagicMock()

                    @api_required()
                    async def cmd(self, interaction):
                        return "OK"

                obj = Dummy()
                mock_interaction = MagicMock()

                assert await obj.cmd(mock_interaction) == "OK"

            @pytest.mark.asyncio
            async def test_unavailable(self):
                """ Test that api_required blocks execution and sends an embed if the API is unavailable. """
                
                class Dummy:
                    def __init__(self):
                        self.lucy = MagicMock()
                        self.lucy.api = None

                    @api_required()
                    async def cmd(self, interaction):
                        return "OK"

                obj = Dummy()
                mock_interaction = MagicMock()
                mock_interaction.response.send_message = AsyncMock()

                await obj.cmd(mock_interaction)
                mock_interaction.response.send_message.assert_called_once()
                args, kwargs = mock_interaction.response.send_message.call_args
                assert isinstance(kwargs.get('embed'), Embed)

            @pytest.mark.asyncio
            async def test_custom_description(self):
                """ Test that api_required uses the custom description in the embed. """

                class Dummy:
                    def __init__(self):
                        self.lucy = MagicMock()
                        self.lucy.api = None

                    @api_required(description = "Check your dashboard")
                    async def cmd(self, interaction):
                        pass

                obj = Dummy()
                mock_interaction = MagicMock()
                mock_interaction.response.send_message = AsyncMock()

                await obj.cmd(mock_interaction)
                args, kwargs = mock_interaction.response.send_message.call_args
                embed = kwargs.get('embed')
                assert "Check your dashboard" in embed.description

        class TestRestrictToAuthor:
            @pytest.mark.asyncio
            async def test_allowed(self):
                """ Test that restrict_to_author allows interaction if the user is the author. """
                
                mock_author = MagicMock(id = 123)
                
                class DummyComponent:
                    def __init__(self):
                        self.shared = False
                        self.author = mock_author

                    @restrict_to_author
                    async def callback(self, interaction):
                        return "Executed"

                comp = DummyComponent()
                mock_interaction = MagicMock()
                mock_interaction.user = mock_author
                
                assert await comp.callback(mock_interaction) == "Executed"

            @pytest.mark.asyncio
            async def test_blocked(self):
                """ Test that restrict_to_author blocks interaction if the user is not the author. """
                
                MagicMock(id = 123)
                MagicMock(id = 987)

            @pytest.mark.asyncio
            async def test_shared_true_allowed_for_stranger(self):
                """ Test that if shared is True, anyone can interact. """

                mock_author = MagicMock(id = 123)
                mock_stranger = MagicMock(id = 987)
                
                class DummyComponent:
                    def __init__(self):
                        self.shared = True
                        self.author = mock_author

                    @restrict_to_author
                    async def callback(self, interaction):
                        return "Executed"

                comp = DummyComponent()
                mock_interaction = MagicMock()
                mock_interaction.user = mock_stranger
                
                assert await comp.callback(mock_interaction) == "Executed"
                
                class DummyComponent:
                    def __init__(self):
                        self.shared = False
                        self.author = mock_author

                    @restrict_to_author
                    async def callback(self, interaction):
                        return "Executed"

                comp = DummyComponent()
                mock_interaction = MagicMock()
                mock_interaction.user = mock_stranger
                mock_interaction.response.send_message = AsyncMock()

                result = await comp.callback(mock_interaction)
                
                assert result != "Executed"
                mock_interaction.response.send_message.assert_called_once_with(
                    "You can't interact with this component.",
                    ephemeral = True
                )

