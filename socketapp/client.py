from __future__ import annotations

import asyncio
import json
import logging
import signal
import typing as t

from websockets.legacy.client import WebSocketClientProtocol, connect

from socketapp.event import Event

LOG = logging.getLogger(__file__)


class Client:
    def __init__(
        self, host: str = "localhost", port: int = 5000, password: str | None = None
    ) -> None:
        self.host = host
        self.port = port

        self.password = password

        self.future: asyncio.Future[bool] | None = None
        self.client_id: int | None = None
        self.ws: WebSocketClientProtocol | None = None

        self.clients: set[int] = set()

    @property
    def uri(self) -> str:
        return f"ws://{self.host}:{self.port}"

    async def run(self) -> None:
        asyncio.get_event_loop().add_signal_handler(signal.SIGINT, self.stop)

        if not self.future or self.future.done():
            self.future = asyncio.Future()

        async with connect(self.uri) as ws:
            self.ws = ws
            self.client_id = await self._handshake(ws)
            asyncio.create_task(self._process_messages(ws))

            await self.future

    def stop(self) -> None:
        if self.future and not self.future.done():
            self.future.set_result(False)

    async def send(self, event: Event, to: t.Collection[int]) -> None:
        assert self.ws and self.client_id is not None, "client is not ready"

        to = set(to)
        if event.process_locally and self.client_id in to:
            to.remove(self.client_id)
            if not await event.process_client(self, self.client_id):
                return

        raw = json.dumps({"to": list(to), "event": event.to_dict()})
        await self.ws.send(raw)

    async def _handshake(self, ws: WebSocketClientProtocol) -> int:
        await ws.send(json.dumps({"password": self.password}))
        return int(json.loads(await ws.recv())["client_id"])

    async def _process_messages(self, ws: WebSocketClientProtocol) -> None:
        try:
            async for msg in ws:
                asyncio.create_task(self._process_message(msg))
        except Exception as e:
            if self.future and not self.future.done():
                self.future.set_exception(e)
        finally:
            if self.future and not self.future.done():
                self.future.set_result(True)

    async def _process_message(self, data: str | bytes) -> None:
        dct = t.cast("dict[str, t.Any]", json.loads(data))

        if dct.get("system", False):
            self.clients = set(dct["clients"])

        elif event := dct.get("event"):
            await Event.load(event).process_client(self, dct["author_id"])
