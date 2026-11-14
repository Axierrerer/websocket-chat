import logging

from fastapi import APIRouter, Depends, WebSocket
from punq import Container
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from core.container import get_container
from infra.ws_manager import WebSocketConnectionManager
from transport.websocket.schemas import EventSchema

logger = logging.getLogger(__name__)

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


@ws_router.websocket(path="/chats/{chat_id}")
async def ws_chat(
    ws: WebSocket, chat_id: str, container: Container = Depends(get_container)
) -> None:
    ws_manager = container.resolve(WebSocketConnectionManager)
    try:
        await ws_manager.connect(chat_id, ws)
        while True:
            try:
                msg = await ws.receive_text()
                validated_msg = EventSchema.model_validate_json(msg)
                await ws_manager.publish(chat_id, validated_msg.model_dump_json())
            except ValidationError as e:
                logger.error("Validation error for chat_id: %s", chat_id, exc_info=e)
    except WebSocketDisconnect as e:
        logger.warning("WebSocket for chat_id: %s disconnect error", chat_id, exc_info=e)
    finally:
        await ws_manager.disconnect(chat_id, ws)
