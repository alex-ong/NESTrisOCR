import asyncio
import websockets
import queue
import threading

# We should use auto-bahn server instead, however it uses IF_ANY instead of IF_LOOPBACK
# when hosting. This means firewall error shows up. The app still works, but this
# is user unfriendly. As a result, we are using a different library for now.
# When Autobahn allows hosting on 127.0.0.1 without raising firewall, this dependency
# will be removed.

# This implementation is strictly 1:1 client server. If you add more clients, behavior is
# undefined until we fix it :)


def CreateClient(target, port):
    client = Connection(target, port)
    client.start()
    return client


class Connection(threading.Thread):
    def __init__(self, target, port):
        super().__init__()
        self.host = target
        self.port = port
        self.running = False
        self.queue = queue.Queue()
        self.websockets = set()  # client websockets
        self.server_task = None
        self.loop = None

    def sendMessage(self, data, isBinary=False):
        if not isBinary:
            data = data.encode("utf8")
        self.queue.put(data)

    def checkNetworkClose(self):
        return False

    def close(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def stop(self):
        self.close()

    def run(self):
        if self.running:
            return
        self.running = True

        # note this doesnt work in linux; it should run in main thread.
        # we need self.loop.run_forever() but nonblocking in main thread.

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.broadcast())
        # next, we need to startup our server
        self.server_task = websockets.serve(
            self.on_client_connect, self.host, self.port
        )

        self.loop.run_until_complete(self.server_task)
        self.loop.run_forever()

    async def on_client_connect(self, websocket, path):
        print("client connected")
        self.websockets.add(websocket)
        try:
            # receive messages from clients and ignore them
            async for msg in websocket:
                pass
        except websockets.ConnectionClosed:
            print("Client disconnected")
        finally:
            self.websockets.remove(websocket)

    async def broadcast(self):
        while True:
            try:
                item = self.queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.016)
                continue
            await asyncio.gather(
                *[ws.send(item) for ws in self.websockets], return_exceptions=False,
            )
