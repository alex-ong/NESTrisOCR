import json
import time
import sys

#sends json messages across network
#sends only when there is change or more than a time period has elapsed  


class CachedSender(object):
    RATE = 0.064
    def __init__(self, client):
        self.client = client
        self.lastMessage = None
        self.lastSend = time.time()
        #self.replayfile = open('replay.txt','a')
        self.startTime = time.time()
    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):             
        timeless_message = json.dumps(message,indent=2)                
        t = time.time()
        if t - self.lastSend > self.RATE or (self.lastMessage != timeless_message):            
            message['time'] = t - self.startTime
            #print(timeless_message)
            time_message = json.dumps(message) #have to redump to insert time
            
            self.client.sendMessage(time_message)
            
            self.lastMessage = timeless_message
            self.lastSend = time.time()
            #self.replayfile.write(time_message + '\n')
            