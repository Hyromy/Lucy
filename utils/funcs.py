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
