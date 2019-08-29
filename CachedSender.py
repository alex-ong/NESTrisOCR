import json
import time

#sends json messages across network
#sends only when there is change or more than a time period has elapsed  
class CachedSender(object):
    RATE = 0.064
    def __init__(self, client):
        self.client = client
        self.lastMessage = None
        self.lastSend = time.time()
        
    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):     
        jsonMessage = json.dumps(message,indent=2)        
        t = time.time()
        if t - self.lastSend > self.RATE or (self.lastMessage != jsonMessage):            
            print(message)
            self.client.sendMessage(jsonMessage)
            self.lastMessage = jsonMessage
            self.lastSend = time.time()