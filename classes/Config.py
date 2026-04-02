import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from json import loads
from dotenv import load_dotenv

from utils.logger import logger

class ConfigErr(Exception):
    pass

class Config:
    def __init__(self, prefix: str = ","):
        load_dotenv()

        self.PREFIX = prefix
        self.PRODUCTION = os.getenv("PRODUCTION", "False") == "True"
        self.API_REST = os.getenv("API_REST", "http://localhost:8000/")
        self.RELEASES_URL = os.getenv("RELEASES_URL")
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        self.PREFIX = prefix
        self.VERSION = None

        self._sync_version()

        if self.PRODUCTION:
            self.TOKEN = os.getenv("DISCORD_BOT_TOKEN")
            if not self.TOKEN:
                raise ConfigErr("Missing DISCORD_BOT_TOKEN for PRODUCTION environment.")
        else:
            self.TOKEN = os.getenv("TESTING_DISCORD_BOT_TOKEN")
            if not self.TOKEN:
                raise ConfigErr("Missing TESTING_DISCORD_BOT_TOKEN for development/testing environment.")

            self.TESTING_GUILD_ID = os.getenv("TESTING_GUILD_ID")
            if not self.TESTING_GUILD_ID:
                raise ConfigErr("Missing TESTING_GUILD_ID for development/testing environment.")

    def _sync_version(self):
        if not self.RELEASES_URL:
            logger.warning("No RELEASES_URL found; version info will be unavailable.")
            return

        headers = {}
        if self.GITHUB_TOKEN:
            headers["Authorization"] = f"token {self.GITHUB_TOKEN}"
        else:
            logger.warning("GITHUB_TOKEN not found in env; proceeding unauthenticated may lead to rate limiting.")

        request = Request(self.RELEASES_URL, headers = headers)
        try:
            with urlopen(request, timeout = 10) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to fetch version info: HTTP {response.status}, {response.reason}.",
                        exc_info = Exception(f"HTTP {response.status}")
                    )
                    return

                payload = loads(response.read().decode("utf-8"))
                self.VERSION = payload.get("tag_name")
                logger.info(f"Version set to {self.VERSION}.")

        except (HTTPError, URLError, TimeoutError) as e:
            logger.error("Timeout or connection error fetching version from GitHub.", exc_info = e)
        except Exception as e:
            logger.error("Unexpected error fetching version from GitHub.", exc_info = e)