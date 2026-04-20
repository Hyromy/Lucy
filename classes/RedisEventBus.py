from os import getenv
from json import JSONDecodeError, loads

from asyncio import CancelledError, Task, create_task
from collections.abc import Awaitable, Callable
import redis.asyncio as redis

from utils.logger import logger


EventCallback = Callable[[str, dict], Awaitable[None]]


class RedisEventBus:
    def __init__(self, redis_url: str | None = None, *, pattern: str | None = None):
        self._redis_url = redis_url or getenv("REDIS_URL")
        self._pattern = pattern or getenv("REDIS_EVENT_PATTERN", "lucy.*")

        self._redis = None
        self._pubsub = None
        self._task: Task | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None

    async def start(self, *, on_event: EventCallback) -> bool:
        if self._task:
            return True

        if not self._redis_url:
            logger.warning("REDIS_URL not found in env; Redis event listener disabled.")
            return False

        try:
            self._redis = redis.from_url(self._redis_url)
            self._pubsub = self._redis.pubsub()
            await self._pubsub.psubscribe(self._pattern)
            self._task = create_task(self._listener_loop(on_event=on_event))
        except Exception as e:
            logger.error("Failed to start Redis event listener", exc_info=e)
            await self._close_clients()
            return False

        return True

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except CancelledError:
                pass
            finally:
                self._task = None

        await self._close_clients()

    async def _close_clients(self):
        if self._pubsub:
            try:
                await self._pubsub.close()
            except Exception as e:
                logger.error("Failed to close Redis pubsub", exc_info=e)
            finally:
                self._pubsub = None

        if self._redis:
            try:
                await self._redis.aclose()
            except Exception as e:
                logger.error("Failed to close Redis client", exc_info=e)
            finally:
                self._redis = None

    async def _listener_loop(self, *, on_event: EventCallback):
        try:
            async for message in self._pubsub.listen():
                if message.get("type") != "pmessage":
                    continue

                channel = message.get("channel")
                if isinstance(channel, bytes):
                    channel = channel.decode("utf-8")

                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                if not isinstance(data, str):
                    logger.warning(f"Redis message ignored (non-string payload): {data}")
                    continue

                try:
                    payload = loads(data)
                except JSONDecodeError:
                    logger.warning(f"Redis message ignored (invalid JSON): channel={channel} data={data}")
                    continue

                if not isinstance(payload, dict):
                    logger.warning(f"Redis message ignored (JSON is not object): {payload}")
                    continue

                await on_event(str(channel), payload)
        except CancelledError:
            logger.info("Redis event listener cancelled.")
            raise

        except Exception as e:
            logger.error("Unexpected error in Redis event listener loop", exc_info=e)
