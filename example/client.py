import asyncio

from example.events import Message
from socketapp import Client


async def send(client: Client) -> None:
    while True:
        await asyncio.sleep(5)
        await client.send(Message(data="hi"), client.clients)


async def main(client: Client) -> None:
    asyncio.create_task(send(client))
    await client.run()


try:
    client = Client()
    asyncio.run(main(client))
finally:
    client.stop()
