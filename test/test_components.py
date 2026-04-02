import pytest
from unittest.mock import (
    patch,
    MagicMock,
    AsyncMock,
)

from discord import (
    ButtonStyle,
    SelectOption,
)

from components.cmd.help import (
    GeneralHelpView,
)

from components.elements import (
    BaseButton,
    BaseSelect,
    BaseView,
)

def mock_users_interaction_ctx():
    mock_author = MagicMock(id = 123)
    mock_someone = MagicMock(id = 987)
    mock_callback = AsyncMock()
    mock_interaction = MagicMock()

    mock_interaction.return_value = [mock_someone, mock_author]
    mock_interaction.data = {}

    interaction_someone = MagicMock()
    interaction_someone.user = mock_someone
    interaction_someone.response = MagicMock()
    interaction_someone.response.send_message = AsyncMock()
    interaction_someone.response.edit_message = AsyncMock()
    interaction_someone.data = {}

    interaction_author = MagicMock()
    interaction_author.user = mock_author
    interaction_author.response = MagicMock()
    interaction_author.response.send_message = AsyncMock()
    interaction_author.response.edit_message = AsyncMock()
    interaction_author.data = {}

    return {
        "author": mock_author,
        "someone": mock_someone,
        "callback": mock_callback,
        "interaction": {
            "interaction": mock_interaction,
            "someone": interaction_someone,
            "author": interaction_author
        }
    }

def mock_help_data():
    bot_info = {
        "bot_name": "Lucy",
        "bot_avatar_url": "https://example.com/avatar.png",
        "owner_name": "Owner",
        "owner_avatar_url": "https://example.com/owner.png",
        "version": "1.0.0",
        "slash_cmds_cache": {"help": 123456789}
    }
    cogs_dict = {
        "General": {
            "name": "general",
            "show": True,
            "icon": "🏠",
            "app_commands": ["ping", "help"]
        },
        "Config": {
            "name": "config",
            "show": True,
            "icon": "⚙️",
            "app_commands": ["lang"]
        }
    }
    
    return bot_info, cogs_dict

class TestHelpModule:
    class TestCMDPackage:
        class TestHelp:
            def test_instance(self):
                """ Test that a GeneralHelpView can be instantiated with the required parameters and has the correct attributes. """

                bot_info, cogs_dict = mock_help_data()
                mock_user = MagicMock()
                
                view = GeneralHelpView(bot_info, cogs_dict, mock_user)

                assert len(view.children) >= 2
                assert any(isinstance(c, BaseSelect) for c in view.children)
                assert not view.shared
                assert view.author == mock_user

            def test_instance_with_category(self):
                """ Test that if a GeneralHelpView is instantiated with a category, it includes a back button. """

                bot_info, cogs_dict = mock_help_data()
                mock_user = MagicMock()
                
                view = GeneralHelpView(bot_info, cogs_dict, mock_user, category="General")

                assert any(getattr(c, "is_back", False) for c in view.children)

            @pytest.mark.asyncio
            async def test_on_select(self):
                """ Test that when an option is selected, the on_select method updates the view correctly and calls the appropriate callbacks. """

                bot_info, cogs_dict = mock_help_data()
                mock = mock_users_interaction_ctx()
                
                view = GeneralHelpView(bot_info, cogs_dict, mock["author"])
                
                select = next(c for c in view.children if isinstance(c, BaseSelect))
                
                with patch('components.cmd.help.cog_help_embed'):
                    await view.on_select(mock["interaction"]["author"], ["General"])
                    
                    assert any(opt.value == "General" and opt.default for opt in select.options)
                    assert any(getattr(c, "is_back", False) for c in view.children)
                    mock["interaction"]["author"].response.edit_message.assert_called_once()

            @pytest.mark.asyncio
            async def test_on_back_click(self):
                """ Test that when the back button is clicked, the on_back_click method updates the view correctly and calls the appropriate callbacks. """

                bot_info, cogs_dict = mock_help_data()
                mock = mock_users_interaction_ctx()
                
                view = GeneralHelpView(bot_info, cogs_dict, mock["author"], category="General")
                select = next(c for c in view.children if isinstance(c, BaseSelect))

                with patch('components.cmd.help.general_help_embed'):
                    await view.on_back_click(mock["interaction"]["author"])
                    
                    assert not any(getattr(c, "is_back", False) for c in view.children)
                    assert all(not opt.default for opt in select.options)
                    mock["interaction"]["author"].response.edit_message.assert_called_once()

    class TestElements:
        class TestBaseButton:
            def test_instance(self):
                """ Test that a BaseButton can be instantiated with a label and has the correct attributes. """

                label = "Test Button"
                button = BaseButton(label)

                assert button is not None
                assert button.label == label
                assert isinstance(button.style, ButtonStyle)

            @pytest.mark.asyncio
            async def test_callback(self):
                """ Test that the callback function is called when the button is clicked. """

                mock_callback = AsyncMock()
                button = BaseButton("Test Button", on_click = mock_callback)

                mock_interaction = MagicMock()
                mock_interaction.data = {}

                await button.callback(mock_interaction)

                mock_callback.assert_awaited_once_with(mock_interaction)

            @pytest.mark.asyncio
            async def test_close_button(self):
                """ Test that a button with is_close = True stops the view and deletes the message when clicked. """

                view = BaseView()
                button = BaseButton("Test Button", is_close = True)
                view.append(button)
                
                mock_interaction = MagicMock()
                mock_message = AsyncMock()

                mock_interaction.message = mock_message
                
                with patch.object(view, 'stop') as mock_stop:
                    await button.callback(mock_interaction)
                    
                    mock_stop.assert_called_once()
                    mock_message.delete.assert_awaited_once()

            @pytest.mark.asyncio
            async def test_not_shared_button(self):
                """ Test that a button with shared = False only allows the author to interact with it. """

                mock = mock_users_interaction_ctx()

                button = BaseButton("Test Button",
                    shared = False,
                    author = mock["author"],
                    on_click = mock["callback"]
                )
                
                await button.callback(mock["interaction"]["someone"])
                await button.callback(mock["interaction"]["author"])

                mock["callback"].assert_awaited_once_with(mock["interaction"]["author"])

        class TestBaseSelect:
            def test_instance(self):
                """ Test that a BaseSelect can be instantiated with a placeholder and has the correct attributes. """

                placeholder = "Choose an option"
                select = BaseSelect(placeholder)

                assert select is not None
                assert select.placeholder == placeholder
                assert select.min_values == 1
                assert select.max_values == 1
                assert len(select.options) == 0

            def test_options(self):
                """ Test that options can be passed to the BaseSelect and are set correctly. """

                options = [
                    MagicMock(label = "Option 1", value = "option1"),
                    MagicMock(label = "Option 2", value = "option2"),
                ]

                select = BaseSelect("Choose an option", options = options)

                assert len(select.options) == len(options)
                for opt, mock_opt in zip(select.options, options, strict=False):
                    assert opt.label == mock_opt.label
                    assert opt.value == mock_opt.value

            @pytest.mark.asyncio
            async def test_on_select(self):
                """ Test that the on_select callback is called with the correct values when an option is selected. """

                mock_callback = AsyncMock()

                select = BaseSelect("Choose an option",
                    options = [
                        SelectOption(label = "Option 1", value = "option1"),
                        SelectOption(label = "Option 2", value = "option2"),
                    ],
                    on_select = mock_callback
                )

                mock_interaction = MagicMock()

                selected_values = ["option1"]
                mock_interaction.data = {"values": selected_values}

                await select.callback(mock_interaction)

                mock_callback.assert_awaited_once_with(mock_interaction, selected_values)

            @pytest.mark.asyncio
            async def test_not_shared_select(self):
                """ Test that a select with shared = False only allows the author to interact with it. """

                mock = mock_users_interaction_ctx()

                select = BaseSelect("Choose an option",
                    options = [
                        SelectOption(label = "Option 1", value = "option1"),
                        SelectOption(label = "Option 2", value = "option2"),
                    ],
                    on_select = mock["callback"],
                    shared = False,
                    author = mock["author"]
                )

                await select.callback(mock["interaction"]["someone"])
                await select.callback(mock["interaction"]["author"])

                mock["callback"].assert_awaited_once_with(
                    mock["interaction"]["author"],
                    []
                )

        class TestBaseView:
            def test_instance(self):
                """ Test that a BaseView can be instantiated and has the correct default attributes. """

                view = BaseView()

                assert view is not None
                assert len(view.children) == 0
                assert view.shared
                assert not view.delete_on_timeout
                assert view.timeout is not None

            def test_propagate_attributes(self):
                """ Test that child components inherit the shared and author attributes from the view if not set explicitly. """

                mock_author = MagicMock(id = 123)

                view = BaseView(shared = False, author = mock_author)

                button = BaseButton("Test Button")
                select = BaseSelect("Choose an option")
                other = BaseButton("Other Button", shared = True)

                view.append(button, select, other)

                assert not button.shared
                assert button.author == mock_author
                assert not select.shared
                assert select.author == mock_author
                assert other.shared
                assert other.author == mock_author

            def test_associate_message(self):
                """ Test that the associate_message method sets the message attribute on the view. """

                view = BaseView()
                mock_message = MagicMock()

                assert not hasattr(view, "message")

                view.associate_message(mock_message)

                assert hasattr(view, "message")
                assert view.message == mock_message

            @pytest.mark.asyncio
            async def test_delete_on_timeout(self):
                """ Test that if delete_on_timeout is True, the view deletes the associated message when it times out. """

                view = BaseView(delete_on_timeout = True)
                mock_message = AsyncMock()

                view.associate_message(mock_message)

                with patch.object(view, 'stop') as mock_stop:
                    await view.on_timeout()

                    mock_stop.assert_called_once()
                    mock_message.delete.assert_awaited_once()
                    mock_message.delete.assert_awaited_once()

            @pytest.mark.asyncio
            async def test_on_timeout_callback(self):
                """ Test that if an on_timeout_callback is provided, it is called when the view times out. """

                mock_callback = AsyncMock()

                view = BaseView(on_timeout_callback = mock_callback)

                await view.on_timeout()

                mock_callback.assert_awaited_once()
