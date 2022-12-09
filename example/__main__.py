import sys

from example import client, server

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "client":
            client.run()
            exit(0)
        elif sys.argv[1] == "server":
            server.run()
            exit(0)
    print("Usage: python -m example [client|server]")
    exit(-1)
