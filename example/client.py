import asyncio
from concurrent.futures import ThreadPoolExecutor

from example.events import Message
from socketapp import Client


async def send(client: Client) -> None:
    await client.wait_until_ready()
    while True:
        with ThreadPoolExecutor(1, "AsyncInput") as executor:
            inp = await asyncio.get_event_loop().run_in_executor(executor, input)

        # in python 3.9+, you can do this instead:
        # inp = await asyncio.to_thread(input)

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
