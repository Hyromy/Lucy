from asyncio import run
from classes.Lucy import Lucy
from classes.Config import Config, ConfigErr
from discord import Intents
from lang import l
from utils.logger import logger

def lang_key_gen():
    try:
        l.generate_keys()
    except Exception as e:
        logger.error("Error generating keys.py", exc_info = e)
    else:
        logger.info("Generated keys.py successfully.")

def prepare():
    try:
        config = Config()
    
    except ConfigErr as e:
        logger.error(f"Configuration error: {e}")
        exit(1)

    intents = Intents.default()
    intents.message_content = True

    lucy = Lucy(intents, config = config)

    return lucy, config.TOKEN

async def main(lucy: Lucy, token: str):
    await lucy.setup()
    await lucy.start(token)

async def close(lucy: Lucy):
    await lucy.close()

if __name__ == "__main__":
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
    
