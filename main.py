from asyncio import run, sleep
from classes.Lucy import Lucy
from dotenv import load_dotenv
from utils.logger import logger

lucy: Lucy = None

async def main():
    global lucy
    lucy = Lucy()
    await lucy.load_cogs()
    await lucy.start()

if __name__ == "__main__":
    load_dotenv()

    exception = None
    try:
        run(main())

    except KeyboardInterrupt as e:
        logger.info("Program interrupted by user. Exiting...")
        exception = e

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=e)
        exception = e

    if exception is not None and lucy is not None:
        run(lucy.close())
        run(sleep(1))
