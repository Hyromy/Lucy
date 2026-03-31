from asyncio import run
from classes.Lucy import Lucy
from dotenv import load_dotenv
from utils.logger import logger
from os import getenv
from discord import Intents

def prepare():
    production = getenv("PRODUCTION", "False") == "True"
    token = getenv(
        ("" if production else "TESTING_") + "DISCORD_BOT_TOKEN"
    )

    intents = Intents.default()
    intents.message_content = True

    lucy = Lucy(",", intents,
        is_production = production,
        testing_guild_id = getenv("TESTING_GUILD_ID"),
    )

    return lucy, token

async def main(lucy: Lucy, token: str):
    await lucy.setup()
    await lucy.start(token)

async def close(lucy: Lucy):
    await lucy.close()

if __name__ == "__main__":
    load_dotenv()
    lucy, token = prepare()
    
    try:
        run(main(lucy, token))

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Shutting down gracefully.")

    except Exception as e:
        logger.error("Unexpected error in main program", exc_info = e)

    finally:
        run(close(lucy))
