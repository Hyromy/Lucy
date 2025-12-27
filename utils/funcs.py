from json import load
from os import listdir
from re import match as re_match
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

def get_linear_json_value(composed_key: str, json_path: str) -> Any | None:
    """Retrieves the value from a JSON file based on the composed key (split by dots).
    Args:
        composed_key (str): The composed key in the format "Category.Command.Environment".
        json_path (str, optional): The path to the JSON file. Defaults to "data/slash_cmds_id.json".
    
    Returns:
        (str | None): The slash command ID if found, otherwise None.
    
    Example:
        If the JSON file `data/slash_cmds_id.json` contains:
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
        Then calling `get_slash_cmd_id("general.ping.test", "data/slash_cmds_id")` will return `"123"`.
    """
    assert isinstance(composed_key, str), "composed_key must be a string"
    assert isinstance(json_path, str), "json_path must be a string"
    json_path += ".json" if not json_path.endswith(".json") else ""

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

def get_supported_languages(json_path: str = "lang/_settings.json") -> dict:
    """Retrieves the list of supported languages from the settings JSON file.
    Args:
        json_path (str, optional): The path to the settings JSON file. Defaults to "lang/_settings.json".
    
    Returns:
        dict: A dictionary of supported languages.
    """
    assert isinstance(json_path, str), "json_path must be a string"

    with open(json_path, "r", encoding="utf-8") as f:
        return load(f)

def get_lang_package(dir: str = "lang") -> dict:
    """
    Loads language files from the specified directory and returns a dictionary
    mapping language codes to their respective data.
    Only files matching the pattern '^[a-z]{2}\.json$' are considered.

    Args:
        dir (str): The directory containing language JSON files.

    Returns:
        dict: A dictionary where keys are language codes and values are the loaded JSON data.
    """

    assert isinstance(dir, str), "dir must be a string"

    langs = dict()
    for lang_file in listdir(dir):
        if re_match(r"^[a-z]{2}\.json$", lang_file):
            with open(f"{dir}/{lang_file}", "r", encoding = "utf-8") as f:
                langs[lang_file[:-5]] = load(f)

    return langs
