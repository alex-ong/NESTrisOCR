import socketserver
import socket
import struct


from nestris_ocr.network.stoppablethread import StoppableThread

INT_SIZE = 4


def CreateServer(target, port, onRecvMessage):
    server = ThreadedServer(target, port, onRecvMessage)
    server.start()
    print("TCP server started on port " + str(port))
    return server


class ThreadedServer(StoppableThread):
    # todo: currently if mainthread dies, calling threadedServer.stop() won't stop the internal server.
    # this means we have a hanging thread. We should fix this.
    def __init__(self, target, port, onRecvMessage, *args):
        super().__init__()
        self.target = target
        self.port = port
        self.onRecvMessage = onRecvMessage

    def run(self):
        self.server = socketserver.ThreadingTCPServer(
            (self.target, self.port), MyTCPHandler
        )
        self.server.onRecvMessage = self.onRecvMessage
        self.server.serverThreadAlive = self.isAlive
        try:
            self.server.serve_forever(0.5)
        except OSError:  # OSError occurs on server_close()
            pass

    def kill_server(self):
        self.server.server_close()


class MyTCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        # turn off nagles
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        # reuse
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def handle(self):
        # potential improvement - dont use python strings as buffer
        dataBuffer = b""
        while self.server.serverThreadAlive():
            try:
                data = self.request.recv(1024)

                if not data:
                    break  # disconnection

                dataBuffer += data
                while len(dataBuffer) >= INT_SIZE:
                    header = dataBuffer[:INT_SIZE]
                    data_len = struct.unpack("<i", header)[0]
                    target_idx = data_len + INT_SIZE
                    if len(dataBuffer) < target_idx:
                        break

                    msg = dataBuffer[INT_SIZE:target_idx]
                    dataBuffer = dataBuffer[target_idx:]
                    self.server.onRecvMessage(msg)

            except ConnectionResetError:
                print("Client disconnected!")
                break
        print("Done handling client!")


if __name__ == "__main__":
    CreateServer("localhost", 9999, print)
