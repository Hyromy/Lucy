from json import load
from os import listdir
from re import match as re_match

def get_lang_package(dir: str = "lang") -> dict:
    r"""
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
