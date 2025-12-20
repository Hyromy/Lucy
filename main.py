from asyncio import run

from dotenv import load_dotenv

from utils.Lucy import Lucy
from utils.Printer import Printer

async def main():
    lucy = Lucy()
    await lucy.load_cogs()
    await lucy.start()

if __name__ == "__main__":
    printer = Printer()
    load_dotenv()

    try:
        run(main())

    except KeyboardInterrupt:
        printer.info("Program interrupted by user. Exiting...")

    except Exception as e:
        printer.error(f"An unexpected error occurred: {e}")
