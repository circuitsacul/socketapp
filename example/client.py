import asyncio
import sys

from example.events import Message
from socketapp import Client

if sys.version_info < (3, 9, 0):
    from concurrent.futures import ThreadPoolExecutor


async def send(client: Client) -> None:
    await client.wait_until_ready()
    while True:
        if sys.version_info < (3, 9, 0):
            with ThreadPoolExecutor(1, "AsyncInput") as executor:
                inp = await asyncio.get_event_loop().run_in_executor(executor, input)
        else:
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
