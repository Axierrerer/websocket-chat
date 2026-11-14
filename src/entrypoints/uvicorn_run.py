import asyncio
import contextlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.container import get_container
from core.settings import AllSettings
from infra.redis.client import AsyncRedis
from infra.redis.listener import RedisListener
from transport.websocket.handlers import ws_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    redis_listener = get_container().resolve(RedisListener)
    listener_task = asyncio.create_task(redis_listener.process_message())
    yield
    listener_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await listener_task
    redis = get_container().resolve(AsyncRedis)
    await redis.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(ws_router)
    return app


async def main() -> None:
    settings = get_container().resolve(AllSettings)
    config = uvicorn.Config(
        create_app,
        factory=True,
        host=settings.app.HOST,
        port=settings.app.PORT,
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
