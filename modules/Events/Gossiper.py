from discord.ext import commands

from classes.Lucy import Lucy
from classes.RedisEventBus import RedisEventBus
from utils.logger import logger

class Gossiper(commands.Cog):
    def __init__(self, lucy: Lucy):
        self.lucy = lucy
        self._redis_bus = RedisEventBus()

        self._supported_models = {
            "guild",
        }
        self._supported_events = {
            "created",
            "updated",
            "deleted"
        }

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.start_redis_listener()
        except Exception as e:
            logger.error("Failed to start Redis listener", exc_info=e)
        else:
            logger.info("Redis listener started successfully.")

    async def start_redis_listener(self):
        await self._redis_bus.start(on_event = self.on_redis_message)

    async def on_redis_message(self, channel: str, payload: dict):
        channel_parts = channel.split(".")
        model = channel_parts[1]
        action = channel_parts[2]

        if (
            model not in self._supported_models
            or action not in self._supported_events
        ):
            logger.warning(f"Received unsupported Redis event: {channel}")
            return

        method_name = f"on_redis_{model}_{action}"
        method = getattr(self, method_name, None)

        if method:
            method(payload)
        else:
            logger.warning(f"Unhandled Redis event: {channel}")

    def _update_guild_cache(self, payload: dict):
        guild_id = payload["id"]
        self.lucy.cache["guilds"][guild_id] = payload

    def on_redis_guild_created(self, payload: dict):
        self._update_guild_cache(payload)

    def on_redis_guild_updated(self, payload: dict):
        self._update_guild_cache(payload)

    def on_redis_guild_deleted(self, payload: dict):
        self.lucy.cache["guilds"].pop(payload["id"], None)

    async def stop_redis_listener(self):
        await self._redis_bus.stop()

    def cog_unload(self):
        if not self._redis_bus.is_running:
            return

        try:
            loop = getattr(self.lucy, "loop", None)
            if loop is None or loop.is_closed():
                return

            loop.create_task(self.stop_redis_listener())
        except Exception as e:
            logger.error("Failed to schedule Redis listener shutdown", exc_info=e)

async def setup(lucy: Lucy):
    await lucy.add_cog(Gossiper(lucy))
