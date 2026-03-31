from typing import (
    Callable,
    Awaitable,
    Any
)

from discord import (
    ButtonStyle,
    Interaction,
    User,
    Message,
)
from discord.ui import (
    Button,
    Select,
    View,
)

from decorators.validations import restrict_to_author
from utils.logger import logger

class BaseButton(Button):
    r"""
    A base button class that can be extended for custom behavior.

    Args:
        label (str): The text to display on the button.
        shared (bool): Whether the button is shared across users or restricted to the author.
        author (User): The user who is allowed to interact with the button if not shared.
        on_click (Callable[[Interaction], Awaitable[Any]]): An optional async function to call when the button is clicked.
        style (ButtonStyle): The style of the button.

    Examples:
    ```
        async def my_callback(interaction: Interaction):
            await interaction.response.send_message("Button clicked!")

        btn = BaseButton("Click Me",
            shared = True,
            on_click = my_callback
        )
    ```
    """

    def __init__(self, label: str, /, *,
        shared: bool = None,
        author: User = None,
        on_click: Callable[[Interaction], Awaitable[Any]] = None,
        
        style: ButtonStyle = ButtonStyle.primary,
        
        **kwargs
    ):
        super().__init__(
            label = label,
            style = style,
            **kwargs
        )

        self.shared = shared
        self.author = author
        self.on_click = on_click

    @restrict_to_author
    async def callback(self, interaction: Interaction):
        if self.on_click:
            return await self.on_click(interaction)

class BaseSelect(Select):
    r"""
    A base select class that can be extended for custom behavior.

    Args:
        placeholder (str): The placeholder text for the select.
        min_values (int): Minimum number of options that must be selected.
        max_values (int): Maximum number of options that can be selected.
        options (list): The options for the select.
        on_select (Callable[[Interaction, list[str]], Awaitable[Any]]): An optional async function to call when the select is used.

    Examples:
    ```
        async def my_callback(interaction: Interaction, values: list[str]):
            await interaction.response.send_message(f"Seleccionaste: {', '.join(values)}")

        select = BaseSelect(
            placeholder = "Choose an option",
            options = [...],
            on_select = my_callback
        )
    ```
    """
    def __init__(self, placeholder: str, /, *,
        shared: bool = None,
        author: User = None,
        on_select: Callable[[Interaction, list[str]], Awaitable[Any]] = None,

        min_values: int = 1,
        max_values: int = 1,
        options: list = [],

        **kwargs
    ):
        super().__init__(
            placeholder = placeholder,
            min_values = min_values,
            max_values = max_values,
            options = options,
            **kwargs
        )

        self.shared = shared
        self.author = author
        self.on_select = on_select

    @restrict_to_author
    async def callback(self, interaction: Interaction):
        if self.on_select:
            return await self.on_select(
                interaction,
                interaction.data.get("values", [])
            )

class BaseView(View):
    r"""
    Base class for creating custom Discord UI Views.

    Allows you to set the `shared` and `author` attributes for all child components (buttons, selects, etc). If a component supports these attributes and does not define them explicitly, it will inherit the value from the view. If the component defines them, they will NOT be overwritten.

    Supports optional timeout callbacks:
    - `before_timeout`: async function executed before the view times out (useful for cleanup or pre-timeout actions).
    - `after_timeout`: async function executed after the view times out (useful for logging, notifications, etc).

    - If `shared` is True (default), anyone can interact with the components.
    - If `shared` is False and `author` is set, only that user can interact.

    Args:
        *items: Components to add to the view (e.g., buttons, selects).
        shared (bool): Whether the components are shared among users or restricted to the author. Default is True.
        author (User): The user allowed to interact if not shared. Default is None.
        delete_on_timeout (bool): Whether to delete the associated message when the view times out. Default is False.
        before_timeout (Callable[[], Awaitable[Any]]): Optional async callback before timeout.
        after_timeout (Callable[[], Awaitable[Any]]): Optional async callback after timeout.
        timeout (int): Time in seconds before the view times out. Default is 180.

    Example:
    ```python
    view = BaseView(
        BaseButton(label="Shared Button"),
        BaseButton(label="Another Button"),
        BaseButton(label="Author Only", shared=False, author=some_user),
    )
    ```
    """

    def __init__(self, *items: Any,
        shared: bool = True,
        author: User = None,
        delete_on_timeout: bool = False,
        before_timeout: Callable[[], Awaitable[Any]] = None,
        after_timeout: Callable[[], Awaitable[Any]] = None,

        timeout: int = 180
    ):
        super().__init__(timeout = timeout)
        self.shared = shared
        self.author = author
        self.delete_on_timeout = delete_on_timeout
        self.before_timeout = before_timeout
        self.after_timeout = after_timeout

        self.append(*items)

    def append(self, *items):
        r"""
        Add components to the view.

        Example:
        ```python
        view = BaseView(BaseButton("Button 1"))
        view.append(
            BaseButton("Button 2"),
            BaseButton("Button 3")
        )
        ```
        """
        for item in items:
            if self.shared is not None:
                if hasattr(item, 'author') and getattr(item, 'author', None) is None:
                    item.author = self.author
                if hasattr(item, 'shared') and getattr(item, 'shared', None) is None:
                    item.shared = self.shared
            super().add_item(item)

    def associate_message(self, message: Message):
        r"""
        Associates a Discord message with this view.

        This method is only necessary if you need to manually set the message for features like `delete_on_timeout`, or if you want to edit/delete the message later. In most cases, Discord automatically assigns `self.message` to the view when you use `Message.edit(view=...)` or `Interaction.followup.send(view=...)`.

        However, if you send the view with `channel.send(...)` or `Interaction.response.send_message(...)`, you must call this method manually, as Discord does not automatically set `self.message` in those cases.

        Args:
            message (Message): The Discord message to associate with this view.

        Example:
        ```python
            view = BaseView(BaseButton("Click Me"), delete_on_timeout=True)
            msg = await channel.send("This message will be deleted when the view times out.", view=view)
            view.associate_message(msg)
        ```
        """

        self.message = message

    async def on_timeout(self):
        if self.before_timeout:
            try:
                await self.before_timeout()
            except Exception as e:
                logger.error("Error in before_timeout callback.", exc_info = e)

        if self.delete_on_timeout and hasattr(self, "message") and self.message is not None:
            self.stop()
            await self.message.delete()

        if self.after_timeout:
            try:
                await self.after_timeout()
            except Exception as e:
                logger.error("Error in after_timeout callback.", exc_info = e)
