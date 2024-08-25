from re import search, sub
from os import remove

def get_name(data:str) -> str | None:
    name_re = r"<!--\s*(.+)\s*-->"
    return search(name_re, data).group(1) if search(name_re, data) else None

def get_body(data:str):
    body_re = r"<!--.*-->"
    body = sub(body_re, "", data).strip() if search(body_re, data) else None

    with open("./release_body.md", "w", encoding = "utf-8") as f:
        f.write(body)

def run():
    with open("./releases.md", "r", encoding = "utf-8") as f:
        release_data = f.read()

    release_name = get_name(release_data)
    get_body(release_data)

    if not release_name:
        exit(1)

    with open("./release_body.md", "r", encoding = "utf-8") as f:
        release_body = f.read()

    print(f"::set-output name=release_name::{release_name}")
    print(f"::set-output name=release_body::{release_body}")

    remove("./release_body.md")

if __name__ == "__main__":
    run()