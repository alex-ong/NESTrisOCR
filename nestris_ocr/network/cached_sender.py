import json
import nestris_ocr.utils.time as time
from nestris_ocr.network.byte_stuffer import stuffDictionary

# sends json messages across network
# sends only when there is change or more than a time period has elapsed


class CachedSender(object):
    RATE = 0.064

    def __init__(self, client, pp, protocol):
        self.client = client
        self.lastMessage = None
        self.lastSend = time.time()
        # self.replayfile = open("replay.txt","a")
        self.startTime = time.time()
        self.printPacket = pp
        self.protocol = protocol

    # convert message to jsonstr and then send if its new.
    def sendResult(self, message, timeStamp):
        isSame = sameMessage(self.lastMessage, message)
        t = time.time()
        if t - self.lastSend > self.RATE or (not isSame):
            # print(self.lastMessage,"\n",message)
            self.lastMessage = message.copy()
            message["time"] = timeStamp

            message = prePackMessage(message, self.protocol)

            if self.printPacket:
                print(message)

            packed, binary = packMessage(message, self.protocol)

            self.client.sendMessage(packed, binary)

            self.lastSend = time.time()


def prePackMessage(dictionary, protocol):
    if "field" in dictionary:
        dictionary["field"] = dictionary["field"].serialize()
    return dictionary


def packMessage(dictionary, protocol):
    if protocol in ["LEGACY", "AUTOBAHN", "FILE"]:
        return json.dumps(dictionary), False
    elif protocol in ["AUTOBAHN_V2", "AUTOBAHN_SERVER", "WEBSOCKET_SERVER"]:
        return bytes(stuffDictionary(dictionary)), True


def sameMessage(dict1, dict2):
    if dict1 is None:
        return False

    for key in dict1.keys():
        if key in dict2:
            if dict1[key] != dict2[key]:
                return False
        else:
            return False

    return True
