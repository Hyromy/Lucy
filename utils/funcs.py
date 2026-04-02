import os
import ast

from urllib.parse import urljoin

def normalize_url(base_url: str, endpoint: str, *,
    trailing_slash: bool = True
) -> str:
    r"""
    Normalizes a URL by joining the base URL and endpoint, and ensuring it ends with a slash if specified.

    Args:
        base_url (str): The base URL.
        endpoint (str): The endpoint to join with the base URL.
        trailing_slash (bool): Whether to ensure the URL ends with a slash.

    Returns:
        str: The normalized URL.
    """
    base = base_url.rstrip("/") + "/"
    endpoint = endpoint.strip("/")

    url = urljoin(base, endpoint)

    if trailing_slash:
        if not url.endswith("/"):
            url += "/"
    else:
        url = url.rstrip("/")

    return url

def id_url_param(id: int) -> str:
    r"""
    Converts an integer ID to a string suitable for use in a URL. If the ID is not a valid non-negative integer, returns an empty string.

    Args:
        id (int): The ID to convert.

    Returns:
        str: The string representation of the ID if valid, otherwise an empty string.
    """

    is_valid = isinstance(id, int) and id > 0

    return str(id) if is_valid else ""

def get_cogs_dict(lucy) -> dict:
    """ Generates a dictionary containing information about the cogs in the Lucy bot. """    

    result = {}
    for cog in lucy.cogs.values():
        cog_name = cog.__cog_name__

        app_commands = []
        if hasattr(cog, 'get_app_commands') and callable(cog.get_app_commands):
            app_commands = list(cog.get_app_commands())
        elif hasattr(cog, 'app_commands'):
            app_commands = list(cog.app_commands)

        app_command_names = []
        for cmd in app_commands:
            name = getattr(cmd, 'name', str(cmd))
            app_command_names.append(name)

        result[cog_name] = {
            'name': cog_name.lower(),
            'show': getattr(cog, 'show', False),
            'icon': getattr(cog, 'icon', None),
            'app_commands': app_command_names
        }
    return result

def get_bot_info(lucy) -> dict:
    """ Generates a dictionary containing essential bot information for UI components. """
    
    return {
        "bot_name": lucy.user.name,
        "bot_avatar_url": lucy.user.display_avatar.url,
        "owner_name": lucy.OWNER.name,
        "owner_avatar_url": lucy.OWNER.display_avatar.url,
        "version": lucy.VERSION,
        "slash_cmds_cache": lucy.cache.get('slash_cmds', {})
    }

def count_commands_in_files(directory: str = "modules") -> dict:
    """  Counts the number of app commands in each Python file within the specified directory. This is used to track command counts for caching purposes. """
    command_stats = {}

    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            path = os.path.join(directory, filename)
            cog_name = filename[:-3]
            count = 0

            with open(path, "r", encoding="utf-8") as f:
                try:
                    node = ast.parse(f.read())
                    for n in ast.walk(node):
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            for decorator in n.decorator_list:
                                if isinstance(decorator, ast.Call):
                                    func = decorator.func
                                else:
                                    func = decorator

                                if hasattr(func, 'value') and isinstance(func.value, ast.Name):
                                    if func.value.id == 'app_commands':
                                        count += 1
                                        break
                except SyntaxError:
                    continue

            command_stats[cog_name] = count

    return command_stats
