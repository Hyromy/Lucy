import os
import ast

from re import match as re_match
from urllib.parse import urljoin

def is_valid_cog_filename(filename: str) -> bool:
    """ Checks if a filename is a valid cog file based on its naming convention. """

    return filename.endswith(".py") and re_match(r"^[A-Z][a-zA-Z0-9_]*\.py$", filename) is not None

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
        "version": lucy.CONFIG.VERSION,
        "slash_cmds_cache": lucy.cache.get('slash_cmds', {})
    }

def count_commands_in_files(directory: str = "modules") -> int:
    """  Counts the total number of app commands across all relevant Python files. """
    
    total_count = 0

    for root, _, files in os.walk(directory):
        for filename in files:
            if is_valid_cog_filename(filename):
                path = os.path.join(root, filename)
                
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        node = ast.parse(f.read())
                        for n in ast.walk(node):
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                for decorator in n.decorator_list:
                                    dec_name = ""
                                    if hasattr(decorator, "func") and hasattr(decorator.func, "attr"):
                                        dec_name = decorator.func.attr
                                    elif hasattr(decorator, "attr"):
                                        dec_name = decorator.attr
                                    
                                    if dec_name == "command":
                                        total_count += 1
                                        break
                    except SyntaxError:
                        continue

    return total_count
