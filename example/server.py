import asyncio

from example import events  # noqa
from socketapp import Server


def run() -> None:
    asyncio.run(Server().run())
