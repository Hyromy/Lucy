from re import search, sub

def get_name(data:str) -> str | None:
    name_re = r"<!--\s*(.+)\s*-->"
    return search(name_re, data).group(1) if search(name_re, data) else None

def get_body(data:str) -> str | None:
    body_re = r"<!--.*-->"
    body = sub(body_re, "", data).strip() if search(body_re, data) else None
    return body.replace("\n", "\\n")

def run():
    with open("./releases.md", "r", encoding = "utf-8") as f:
        release_data = f.read()

    release_name = get_name(release_data)
    release_body = get_body(release_data)

    if not (release_name or release_body):
        exit(1)

    print(f"::set-output name=release_name::{release_name}")
    print(f"::set-output name=release_body::{release_body}")

if __name__ == "__main__":
    run()