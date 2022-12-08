from __future__ import annotations

import asyncio
import json
import logging
import signal

from websockets.exceptions import ConnectionClosedOK
from websockets.legacy.server import WebSocketServerProtocol, serve

from socketapp.event import Event

LOG = logging.getLogger(__file__)


class Server:
    def __init__(
        self, host: str = "localhost", port: int = 5000, password: str | None = None
    ) -> None:
        self.host = host
        self.port = port

        self.password = password

        self.clients: dict[int, WebSocketServerProtocol] = {}

        self.future: asyncio.Future[None] = asyncio.Future()

    async def run(self) -> None:
        asyncio.get_event_loop().add_signal_handler(signal.SIGINT, self.stop)

        if self.future.done():
            self.future = asyncio.Future()

        asyncio.create_task(self._broadcast_clients())
        async with serve(self._serve, self.host, self.port):
            await self.future

    def stop(self) -> None:
        self.future.set_result(None)

    async def _handshake(self, ws: WebSocketServerProtocol) -> int | None:
        init = await ws.recv()
        try:
            data = json.loads(init)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        if data.get("password") != self.password:
            return None

        if self.clients:
            client_id = max(self.clients.keys()) + 1
        else:
            client_id = 0
        self.clients[client_id] = ws

        await ws.send(json.dumps({"client_id": client_id}))
        return client_id

    async def _serve(self, ws: WebSocketServerProtocol) -> None:
        client_id = await self._handshake(ws)
        if client_id is None:
            return

        try:
            async for msg in ws:
                asyncio.create_task(self._process_msg(msg, client_id))
        except ConnectionClosedOK:
            pass
        finally:
            self.clients.pop(client_id)

    async def _broadcast_clients(self) -> None:
        while True:
            await asyncio.sleep(5)
            tasks: list[asyncio.Task[None]] = []
            for ws in self.clients.values():
                tasks.append(
                    asyncio.create_task(
                        ws.send(
                            json.dumps(
                                {"system": True, "clients": list(self.clients.keys())}
                            )
                        )
                    )
                )
            await asyncio.gather(*tasks, return_exceptions=False)

    async def _process_msg(self, msg: str | bytes, client_id: int) -> None:
        try:
            data = json.loads(msg)
            event = Event.load(data["event"])
            to = {int(to) for to in data["to"]}
        except Exception as e:
            LOG.debug(f"Unabled to parse event from {client_id}.", exc_info=e)
            return

        ret = await event.process_server(self, client_id, to)
        if not ret:
            return

        to_send = json.dumps({"author_id": client_id, "event": event.to_dict()})

        await asyncio.gather(
            *(ws.send(to_send) for (cid, ws) in self.clients.items() if cid in to),
            return_exceptions=False,
        )
