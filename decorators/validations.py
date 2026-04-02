import inspect
from typing import Any
from functools import wraps

from discord import (
    Embed,
    Interaction,
)

def args_required(_args: list[tuple[Any, Any]] | list[Any] | Any | None = None):
    """
    Validate all, one, or multiple function arguments to ensure they are provided and not falsy.
    
    Args:
        _args: Can be one of the following:
            - None: Validate all arguments.
            - str: Validate a single argument by name.
            - list of str: Validate multiple arguments by their names.
            - list of tuples: Each tuple contains (parameter_name, expected_type) to validate both presence and type.

    Raises:
        ValueError: If a required argument is missing or falsy.
        TypeError: If an argument does not match the expected type.

    Examples:
        ```
            # check all arguments
            @args_required()
            def func_all(a, b, c):
                pass
            
            # only check "a"
            @args_required("a")
            def func_one(a, b):
                pass
            
            # check "a" and "b"
            @args_required(["a", "b"])
            def func_multiple(a, b, c):
                pass
            
            # check "a" as int and "b" as str
            @args_required([("a", int), ("b", str)])
            def func_typed(a, b, c):
                pass
        ```
    """
    def decorator(func):
        sig = inspect.signature(func)

        def raise_falsy(value: Any, name: str):
            if value is None or not value:
                raise ValueError(f"Parameter '{name}' must not be None or falsy.")

        def raise_required(name: str, args: dict[str, Any]):
            if name not in args:
                raise ValueError(f"Parameter '{name}' is required.")

        def check_name_in_args(name: str, args: dict[str, Any]):
            raise_required(name, args)
            raise_falsy(args[name], name)

        # same logic in sync or async
        def helper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # many args
            if isinstance(_args, list):
                # specific types
                if _args and isinstance(_args[0], tuple):
                    for pair in _args:
                        if not isinstance(pair, tuple) or len(pair) != 2:
                            raise ValueError("When providing a list of tuples, each tuple must contain exactly two elements: (parameter_name, expected_type).")

                        raise_required(pair[0], bound_args.arguments)
                        value = bound_args.arguments[pair[0]]
                        if not isinstance(value, pair[1]):
                            raise ValueError(f"Parameter '{pair[0]}' must be of type {pair[1].__name__}.")
                        if pair[1] is str and not value.strip():
                            raise ValueError(f"Parameter '{pair[0]}' must be a non-empty string.")
                
                # simple names
                else:
                    for param_name in _args:
                        if not isinstance(param_name, str):
                            raise ValueError("When providing a list of parameter names, each name must be a string.")

                        check_name_in_args(param_name, bound_args.arguments)
        
            # single arg
            elif _args is not None:
                check_name_in_args(_args, bound_args.arguments)
                
            # no args, check all
            elif _args is None:
                for param_name, _ in sig.parameters.items():
                    if param_name in bound_args.arguments:
                        raise_falsy(bound_args.arguments[param_name], param_name)

        if inspect.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                helper(*args, **kwargs)
                return await func(*args, **kwargs)        
        else:
            def wrapper(*args, **kwargs):
                helper(*args, **kwargs)
                return func(*args, **kwargs)

        return wrapper
    return decorator

def api_required(*,
    title: str = "⚠️ API Unavailable",
    description: str = None,
    color: int = 0xFF0000,
    ephemeral: bool = False
):
    """
    Requires that the API is available before executing a bot command.

    Args:
        title (str): The title of the embed message when the API is unavailable.
        description (str): Additional description to include in the embed message.
        color (int): The color of the embed message.
        ephemeral (bool): Whether the response message should be ephemeral.

    Returns:
        A decorator that checks for API availability before executing the command.

    Examples:
        ```
            from discord.ext.commands import Cog
            from utils.Lucy import Lucy

            class MyCog(Cog):
                def __init__(self, lucy: Lucy):
                    self.lucy = lucy

                @app_commands.command()
                @api_required()
                async def my_command(self, interaction: Interaction):
                    # Only runs if self.lucy.api is available here
                    await interaction.response.defer()
                    await interaction.followup.send(
                        await self.lucy.api.test()
                    )
        ```
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction:Interaction, *args, **kwargs):
            if not self.lucy.api:
                desc = "The API is currently unavailable."
                return await interaction.response.send_message(
                    embed = Embed(
                        title = title,
                        description = desc if description is None else f"{desc[:-1]}, {description}",
                        color = color
                    ),
                    ephemeral = ephemeral
                )
        
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def restrict_to_author(func):
    r"""
    A decorator to restrict interaction with a component to its author unless it's marked as shared.

    The decorated component must have 'shared' and 'author' attributes. If 'shared' is False and 'author' is set, only the author can interact with the component. If 'shared' is True (default), anyone can interact.

    Examples:
    ```
        class SomeButton(Button):
            def __init__(self, label: str, shared: bool = True, author: User = None):
                super().__init__(label=label)
                self.shared = shared
                self.author = author

            @restrict_to_author
            async def callback(self, interaction: Interaction):
                await interaction.response.send_message("You interacted with the button!")

        # anyone can interact with this button
        button_1 = SomeButton("Click Me")

        # only the author can interact with this button
        button_2 = SomeButton("Don't Click Me",
            shared = False,
            author = some_user
        )
    ```
    """

    async def wrapper(self, interaction: Interaction, *args, **kwargs):
        shared = getattr(self, "shared", None)
        author = getattr(self, "author", None)

        if shared is not None and not shared and author is not None:
            if interaction.user != author:
                return await interaction.response.send_message(
                    "You can't interact with this component.",
                    ephemeral = True
                )
        return await func(self, interaction, *args, **kwargs)
    return wrapper
