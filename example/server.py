import asyncio

from example import events  # noqa
from socketapp import Server

asyncio.run(Server().run())
