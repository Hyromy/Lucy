from asyncio import run, sleep

from dotenv import load_dotenv

from utils.Lucy import Lucy
from utils.Printer import Printer

lucy: Lucy = None

async def main():
    global lucy
    lucy = Lucy()
    await lucy.load_cogs()
    await lucy.start()

if __name__ == "__main__":
    printer = Printer()
    load_dotenv()

    exception = None
    try:
        run(main())

    except KeyboardInterrupt as e:
        printer.info("Program interrupted by user. Exiting...")
        exception = e

    except Exception as e:
        printer.error(f"An unexpected error occurred: {e}", e)
        exception = e

    if exception is not None:
        if lucy is not None:
            run(lucy.close())
            run(sleep(100))
