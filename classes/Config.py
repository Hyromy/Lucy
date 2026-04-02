import os
from dotenv import load_dotenv

class ConfigErr(Exception):
    pass

class Config:
    def __init__(self, prefix: str = ","):
        load_dotenv()
        self.PRODUCTION = os.getenv("PRODUCTION", "False") == "True"
        self.PREFIX = prefix

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

        self.API_REST = os.getenv("API_REST", "http://localhost:8000/")
        self.RELEASES_URL = os.getenv("RELEASES_URL")
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        self.PREFIX = prefix