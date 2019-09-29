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

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
try: 
    from Networking import StoppableThread
except ModuleNotFoundError:
    import StoppableThread

import threading
import time
def CreateClient(target, port):    
    client = Connection(target, port)    
    client.start()
    
    return client
    

class MyClientProtocol(WebSocketClientProtocol):

    connections = []
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()    
        MyClientProtocol.connections.append(self)
        
    def onOpen(self):
        print("WebSocket connection open.")


    #called when the server sends us a message.
    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        if reason is not None:
            ("WebSocket connection closed: {0}".format(reason))
    
    @classmethod
    def broadcast_message(cls, data, isBinary=False):  
        for c in set(cls.connections):
            reactor.callFromThread(c.sendMessage, data, isBinary)
    
    @classmethod
    def close_all(cls):
        for c in set(cls.connections):
            reactor.callFromThread(c.sendClose)
        
            
class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    protocol = MyClientProtocol
    closing = False
    def clientConnectionFailed(self, connector, reason):        
        if not MyClientFactory.closing:
            print("Client connection failed .. retrying ..")
            self.retry(connector)

    def clientConnectionLost(self, connector, reason):        
        if not MyClientFactory.closing:
            print("Client connection lost .. retrying ..")
            self.retry(connector)
    

class Connection(threading.Thread):
    def __init__(self,target,port):        
        super().__init__()        
        self.port = port
        self.host = target
        self.factory = MyClientFactory(u"ws://"+target+":"+str(port))
        
    #reactor thread
    def run(self):             
        reactor.connectTCP(self.host, self.port, self.factory)        
        reactor.run(installSignalHandlers=0)
     
    #called from main thread, enqueues to reactor thread
    def sendMessage(self, data, isBinary=False):
        if not isBinary:
            data = data.encode('utf8')
        MyClientProtocol.broadcast_message(data, isBinary)
    
    #called from main thread
    def close(self):
        MyClientFactory.closing = True
        MyClientProtocol.close_all() #adds task to reactor thread
        time.sleep(5)    
        reactor.callFromThread(reactor.stop)
    
    def stop(self):
        self.close()        
        

if __name__ == '__main__':
    import time
    url = "127.0.0.1"
    #url = "ec2-13-237-232-112.ap-southeast-2.compute.amazonaws.com"
    connection = CreateClient(url,3338)    
    
    for i in range (5):     
        time.sleep(1)
        connection.sendMessage(str(i))
    
    connection.close()   
    connection.join()    

