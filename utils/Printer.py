from datetime import datetime, timezone

from rich.console import Console

from .decorators import singleton

@singleton
class Printer:
    def __init__(self):
        self.console = Console()

    def __time(self) -> str:
        return f"[{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}]"

    def ok(self, msg: str) -> None:
        self.console.print(f"{self.__time()}[bold green] {msg}[/bold green]")

    def warn(self, msg: str) -> None:
        self.console.print(f"{self.__time()}[bold yellow] {msg}[/bold yellow]")

    def error(self, msg: str) -> None:
        self.console.print(f"{self.__time()}[bold red] {msg}[/bold red]")

    def operation(self, msg: str) -> None:
        self.console.print(f"{self.__time()}[bold white] {msg}...[/bold white]")

    def info(self, msg: str) -> None:
        self.console.print(f"{self.__time()}[bold blue] {msg}[/bold blue]")
