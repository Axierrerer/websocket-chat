from dataclasses import dataclass

import redis.asyncio as aioredis

from core.settings import AllSettings


@dataclass
class AsyncRedis:
    client: aioredis.Redis

    @classmethod
    def from_settings(cls, settings: AllSettings) -> AsyncRedis:
        return cls(aioredis.Redis.from_url(url=settings.redis.redis_url, decode_responses=True))

    async def close(self) -> None:
        await self.client.aclose()
