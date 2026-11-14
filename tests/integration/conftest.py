import os
import time
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from redis import Redis
from testcontainers.community.redis import RedisContainer

from core.container import get_container
from entrypoints.uvicorn_run import create_app


@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer]:
    with RedisContainer("redis:8.0-alpine") as container:
        os.environ["REDIS_HOST"] = container.get_container_host_ip()
        os.environ["REDIS_PORT"] = str(container.get_exposed_port(6379))
        get_container.cache_clear()
        yield container


@pytest.fixture(scope="session")
def client(redis_container: RedisContainer) -> Generator[TestClient]:
    with TestClient(create_app()) as client:
        redis: Redis = redis_container.get_client()
        while redis.pubsub_numpat() < 1:
            time.sleep(0.01)
        yield client
