import shutil
import os
import json

from github import Github

def get_version() -> str:
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo("Hyromy/Lucy")
    releases = repo.get_releases()

    if releases.totalCount == 0:
        return "Versión desconocida"
    return releases[0].tag_name

def get_terminal_size() -> int:
    terminal_size = shutil.get_terminal_size()
    
    return terminal_size.columns

def draw_spliter(text:str = "", char:str = "-"):
    size = get_terminal_size()
    print(text.center(size, char))

def read_json_file(path:str) -> dict:
    path += ".json"
    with open(path, encoding = "utf-8") as f:
        data = json.load(f)

    return data

def write_json_file(path:str, data:dict):
    path += ".json"
    with open(path, "w", encoding = "utf-8") as f:
        json.dump(data, f, indent = 4)

def get_prefix(Lucy, message) -> str:
    prefix = read_json_file("dbcache/server")
    return prefix[str(message.guild.id)]["prefix"]