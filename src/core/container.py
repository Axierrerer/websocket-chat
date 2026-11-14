from functools import lru_cache

from punq import Container, Scope

from core.settings import AllSettings
from infra.redis.client import AsyncRedis
from infra.redis.listener import RedisListener
from infra.ws_manager import WebSocketConnectionManager


@lru_cache
def get_container() -> Container:
    container = Container()
    container.register(AllSettings, factory=lambda: AllSettings(), scope=Scope.singleton)
    container.register(
        AsyncRedis,
        factory=lambda: AsyncRedis.from_settings(container.resolve(AllSettings)),
        scope=Scope.singleton,
    )
    container.register(
        WebSocketConnectionManager,
        factory=lambda: WebSocketConnectionManager(redis=container.resolve(AsyncRedis).client),
        scope=Scope.singleton,
    )
    container.register(
        RedisListener,
        factory=lambda: RedisListener(
            redis=container.resolve(AsyncRedis).client,
            ws_manager=container.resolve(WebSocketConnectionManager),
        ),
        scope=Scope.singleton,
    )
    return container
