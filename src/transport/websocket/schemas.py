from typing import Any

from pydantic import BaseModel


class EventSchema(BaseModel):
    type: str = "message.send"
    payload: dict[str, Any]


class ErrorSchema(BaseModel):
    type: str = "message.error"
    payload: dict[str, Any]
