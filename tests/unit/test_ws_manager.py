from unittest.mock import AsyncMock

from infra.ws_manager import WebSocketConnectionManager


async def test_send_msg_to_chat_members() -> None:
    manager = WebSocketConnectionManager(redis=AsyncMock())
    ws1, ws2, other = AsyncMock(), AsyncMock(), AsyncMock()
    await manager.connect("1", ws1)
    await manager.connect("1", ws2)
    await manager.connect("2", other)

    await manager.send_msg("1", "hello")

    ws1.send_text.assert_awaited_once_with("hello")
    ws2.send_text.assert_awaited_once_with("hello")
    other.send_text.assert_not_awaited()


async def test_failed_connection_is_dropped() -> None:
    manager = WebSocketConnectionManager(redis=AsyncMock())
    alive, dead = AsyncMock(), AsyncMock()
    dead.send_text.side_effect = RuntimeError("closed")
    await manager.connect("1", alive)
    await manager.connect("1", dead)

    await manager.send_msg("1", "hello")

    alive.send_text.assert_awaited_once_with("hello")
    assert manager._connections["1"] == {alive}


async def test_disconnect() -> None:
    manager = WebSocketConnectionManager(redis=AsyncMock())
    ws = AsyncMock()
    await manager.connect("1", ws)

    await manager.disconnect("1", ws)
    await manager.disconnect("unknown", ws)

    assert "1" not in manager._connections
