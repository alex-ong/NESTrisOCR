###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.internet import reactor
import threading


class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode("utf8")))

        # echo back message verbatim
        # self.sendMessage(payload, isBinary) //dont send back shit.

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class OCRServer(WebSocketServerProtocol):
    connections = []
    closing = False

    def onConnect(self, request):
        print("Client connected: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connecition open.")
        self.connections.append(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode("utf8")))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.connections.remove(self)

    @classmethod
    def broadcast_message(cls, data, isBinary=False):
        for c in set(cls.connections):
            reactor.callFromThread(c.sendMessage, data, isBinary)

    @classmethod
    def close_all(cls):
        for c in set(cls.connections):
            reactor.callFromThread(c.sendClose)


# this is called when we create a server for interacting with clients
def CreateClient(target, port):
    client = Connection(target, port)
    client.start()

    return client


class Connection(threading.Thread):
    def __init__(self, target, port):
        super().__init__()
        self.port = port
        self.host = target
        if target not in ["localhost", "127.0.0.1", "0.0.0.0"]:
            print(
                "Warning, starting up autobahn_server with target not equal to localhost"
            )
        self.url = u"ws://" + target + ":" + str(port)
        self.protocol = OCRServer
        self.running = False

    # reactor thread
    def run(self):
        if self.running:
            return
        factory = WebSocketServerFactory(self.url)
        factory.protocol = OCRServer

        reactor.listenTCP(3338, factory)
        reactor.run(installSignalHandlers=0)  # run in non-mainthread

    # called from main thread, enqueues to reactor thread
    def sendMessage(self, data, isBinary=False):
        if not isBinary:
            data = data.encode("utf8")
        OCRServer.broadcast_message(data, isBinary)

    def checkNetworkClose(self):
        return False

    # called from main thread
    def close(self):
        OCRServer.closing = True
        reactor.callLater(0.1, OCRServer.close_all)  # adds task to reactor thread
        reactor.callLater(1, reactor.stop)

    def stop(self):
        self.close()


if __name__ == "__main__":

    import sys

    from twisted.python import log

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:3338")
    factory.protocol = MyServerProtocol

    reactor.listenTCP(3338, factory)
    reactor.run()
