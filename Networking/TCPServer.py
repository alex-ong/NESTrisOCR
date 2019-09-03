import socketserver
import threading
import socket
try:
    from Networking.StoppableThread import StoppableThread
except:    
    from StoppableThread import StoppableThread
    
        
START_TOKEN = '\x00'    
END_TOKEN = '\x01'
def CreateServer(target, port, onRecvMessage):    
    server = ThreadedServer(target, port, onRecvMessage)    
    server.start()
    print('TCP server started on port ' + str(port))
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
        self.server = socketserver.ThreadingTCPServer((self.target, self.port), MyTCPHandler)        
        self.server.onRecvMessage = self.onRecvMessage        
        self.server.serverThreadAlive = self.isAlive
        try:
            self.server.serve_forever(0.5)
        except OSError: #OSError occurs on server_close()
            pass
    
    def kill_server(self):    
        self.server.server_close()
        
        
class MyTCPHandler(socketserver.BaseRequestHandler):    
        
    def setup(self):
        # turn off nagles
        self.request.setsockopt(socket.IPPROTO_TCP,
                                socket.TCP_NODELAY, True)
        # reuse
        self.request.setsockopt(socket.SOL_SOCKET,
                                socket.SO_REUSEADDR, 1)
    def handle(self):            
        # potential improvement - dont use python strings as buffer                    
        dataBuffer = ''
        while self.server.serverThreadAlive():
            try:                       
                data = self.request.recv(1024)    
                    
                if not data:
                    break  # disconnection 
                
                data = data.decode("utf-8")  # change from array of bytes to utf8 string
                dataBuffer += data
                while END_TOKEN in dataBuffer:
                    endIndex = dataBuffer.index(END_TOKEN)
                    # check for buffer index of start...
                    try:
                        startIndex = dataBuffer.index(START_TOKEN)
                    except:  # malformed packet
                        print ("TCPServerRecv: Malformed packet, no start_token")
                        self.dataBuffer = self.dataBuffer[endIndex + 1:]
                        continue
                    
                    if startIndex > endIndex:  # malformed packet. Delete everyting including endIndex
                        dataBuffer = self.dataBuffer[endIndex + 1:]
                        continue
                    
                    # by this point we have good packet structure.
                    if startIndex != 0:
                        print ('Unhandled exception, flushing dataBuffer...')
                        dataBuffer = ''
                        continue
                    
                    message = dataBuffer[1:endIndex]
                    self.server.onRecvMessage(message)
                    dataBuffer = dataBuffer[endIndex + 1:]
            except ConnectionResetError:
                print ("Client disconnected!")
                break
        print ("Done handling client!")

if __name__ == "__main__":
    CreateServer('localhost', 9999, print)
    
