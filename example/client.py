import asyncio

from example.events import Message
from socketapp import Client


async def send(client: Client) -> None:
    await client.wait_until_ready()
    while True:
        inp = await asyncio.to_thread(input)
        await client.send(Message(data=inp), client.clients)


async def main(client: Client) -> None:
    asyncio.create_task(send(client))
    await client.run()


def run() -> None:
    try:
        client = Client()
        asyncio.run(main(client))
    finally:
        client.stop()
