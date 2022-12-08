from socketapp import Client, Event, Server


class Message(Event):
    event_id = 0
    data: str

    async def process_client(self, client: "Client", author: int) -> bool:
        print(f"{author}: {self.data}")
        return True

    async def process_server(self, server: "Server", author: int, to: set[int]) -> bool:
        print(f"{author} (to {to}): {self.data}")
        return True
