import json

from fastapi.testclient import TestClient

MESSAGE = json.dumps({"type": "message.send", "payload": {"text": "hi"}})


def test_message_delivered_to_chat_members(client: TestClient) -> None:
    with (
        client.websocket_connect("/ws/chats/1") as alice,
        client.websocket_connect("/ws/chats/1") as bob,
    ):
        alice.send_text(MESSAGE)

        assert bob.receive_json() == {"type": "message.send", "payload": {"text": "hi"}}


def test_invalid_message_is_skipped(client: TestClient) -> None:
    with (
        client.websocket_connect("/ws/chats/2") as alice,
        client.websocket_connect("/ws/chats/2") as bob,
    ):
        alice.send_text("not json")
        alice.send_text(MESSAGE)

        assert bob.receive_json()["payload"] == {"text": "hi"}
