from datetime import datetime, timezone
from traceback import format_exception

from rich.console import Console

from decorators.patterns import singleton

@singleton
class Printer:
    def __init__(self):
        self.console = Console()

    def __time(self) -> str:
        return f"[{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}]"

    def ok(self, *msg: str) -> None:
        self.console.print(f"{self.__time()}[bold green] {' '.join([str(m) for m in msg])}[/bold green]")

    def warn(self, *msg: str) -> None:
        self.console.print(f"{self.__time()}[bold yellow] {' '.join([str(m) for m in msg])}[/bold yellow]")

    def error(self, *msg: str, exc: Exception = None) -> None:
        if exc is None and msg and isinstance(msg[-1], BaseException):
            exc = msg[-1]
            msg = msg[:-1]

        full_msg = f"{self.__time()}[bold red] {' '.join([str(m) for m in msg])}[/bold red]"
        if exc:
            full_msg += "\n" + "".join(format_exception(type(exc), exc, exc.__traceback__))
        self.console.print(full_msg)

    def operation(self, *msg: str) -> None:
        self.console.print(f"{self.__time()}[bold white] {' '.join([str(m) for m in msg])}...[/bold white]")

    def info(self, *msg: str) -> None:
        self.console.print(f"{self.__time()}[bold blue] {' '.join([str(m) for m in msg])}[/bold blue]")