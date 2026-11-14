import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import WebSocket
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


@dataclass
class WebSocketConnectionManager:
    redis: Redis
    _connections: dict[str, set[WebSocket]] = field(
        default_factory=lambda: defaultdict(set), init=False
    )

    async def connect(self, chat_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[chat_id].add(ws)

    async def disconnect(self, chat_id: str, ws: WebSocket) -> None:
        connections = self._connections.get(chat_id)
        if connections is None:
            return
        connections.discard(ws)
        if not connections:
            del self._connections[chat_id]

    async def publish(self, chat_id: str, data: str) -> None:
        await self.redis.publish(channel=f"chat:{chat_id}", message=data)

    async def send_msg(self, chat_id: str, data: str) -> None:
        if not self._connections.get(chat_id):
            return
        connections = list(self._connections[chat_id])
        results = await asyncio.gather(
            *[ws.send_text(data) for ws in connections], return_exceptions=True
        )
        for ws, result in zip(connections, results, strict=True):
            if isinstance(result, Exception):
                logger.error(
                    "Exception while sending message to chat_id: %s", chat_id, exc_info=result
                )
                await self.disconnect(chat_id, ws)
