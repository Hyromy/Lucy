from asyncio import run
from classes.Lucy import Lucy
from discord import Intents
from dotenv import load_dotenv
from lang import l
from os import getenv
from utils.logger import logger

def lang_key_gen():
    logger.info("Generating keys.py from base language JSON...")
    try:
        l.generate_keys()
    except Exception as e:
        logger.error("Error generating keys.py", exc_info = e)
    else:
        logger.info("keys.py generated successfully.")


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
        lang_key_gen()
        run(main(lucy, token))

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Shutting down gracefully.")

    except Exception as e:
        logger.error("Unexpected error in main program", exc_info = e)

    finally:
        run(close(lucy))
    
