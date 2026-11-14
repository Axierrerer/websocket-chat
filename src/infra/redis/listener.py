import asyncio
import logging
from dataclasses import dataclass

from redis import ConnectionError
from redis.asyncio import Redis

from infra.ws_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)


@dataclass
class RedisListener:
    redis: Redis
    ws_manager: WebSocketConnectionManager

    async def process_message(self) -> None:
        while True:
            try:
                async with self.redis.pubsub(ignore_subscribe_messages=True) as pubsub:
                    await pubsub.psubscribe("chat:*")
                    async for msg in pubsub.listen():
                        chat_id = msg["channel"].removeprefix("chat:")
                        await self.ws_manager.send_msg(chat_id, msg["data"])
            except ConnectionError as e:
                logger.error("Connection error: %s", e, exc_info=e)
                await asyncio.sleep(1)
