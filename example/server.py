import asyncio

from example import events
from socketapp import Server


async def send_hello(server: Server) -> None:
    while True:
        await server.send(events.Message(data="Hello from the server!"), server.clients)
        await asyncio.sleep(10)


async def main(server: Server) -> None:
    asyncio.create_task(send_hello(server))
    await server.run()


def run() -> None:
    try:
        server = Server()
        asyncio.run(main(server))
    finally:
        server.stop()
