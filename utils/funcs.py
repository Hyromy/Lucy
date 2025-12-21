from json import load
from typing import Any

def possessive(word: str, lang: str = "en") -> str:
    """Returns the possessive form of a word in the specified language.
    Args:
        word (str): The word to convert to possessive form.
        lang (str, optional): The language code. Defaults to "en" (English).

    Returns:
        str: The possessive form of the word.
    """
    assert isinstance(word, str), "word must be a string"
    assert isinstance(lang, str), "lang must be a string"

    match lang.lower():
        case "en":
            return word + ("'" if word.endswith("s") else "'s")
        
        case "es":
            return "de " + word

        case _:
            return word

def get_linear_json_value(composed_key: str, json_path: str = "data/slash_cmds_id.json") -> Any | None:
    """Retrieves the value from a JSON file based on the composed key (split by dots).
    Args:
        composed_key (str): The composed key in the format "Category.Command.Environment".
        json_path (str, optional): The path to the JSON file. Defaults to "data/slash_cmds_id.json".
    
    Returns:
        (str | None): The slash command ID if found, otherwise None.
    
    Example:
        If the JSON file contains:
        ```
        {
            "general": {
                "ping": {
                    "test": "123",
                    "prod": "987"
                }
            }
        }
        ```
        Then calling `get_slash_cmd_id("general.ping.test")` will return `"123"`.
    """
    assert isinstance(composed_key, str), "composed_key must be a string"
    assert isinstance(json_path, str), "json_path must be a string"

    with open(json_path, "r", encoding="utf-8") as f:
        data = load(f)

    keys = composed_key.split(".")
    current_level = data
    for key in keys:
        if isinstance(current_level, dict) and key in current_level:
            current_level = current_level[key]
        else:
            return None
    return current_level if isinstance(current_level, str) else None
