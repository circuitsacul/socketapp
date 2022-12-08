from __future__ import annotations

import json
import typing as t

import pydantic

if t.TYPE_CHECKING:
    from socketapp.client import Client
    from socketapp.server import Server


class Event(pydantic.BaseModel):
    event_map: t.ClassVar[dict[int, type["Event"]]] = {}

    event_id: t.ClassVar[int]
    process_locally: t.ClassVar[bool] = True

    def __init_subclass__(cls) -> None:
        assert cls.event_id is not None
        assert cls.event_id not in Event.event_map

        Event.event_map[cls.event_id] = cls

    async def process_server(self, server: "Server", author: int, to: set[int]) -> bool:
        return True

    async def process_client(self, client: "Client", author: int) -> bool:
        return True

    def to_dict(self) -> dict[str, t.Any]:
        dct = super().dict()
        dct["cls_id"] = self.event_id
        return dct

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def load(data: dict[str, t.Any] | str) -> "Event":
        if isinstance(data, str):
            data = t.cast("dict[str, t.Any]", json.loads(data))
        return Event.event_map[data.pop("cls_id")](**data)
