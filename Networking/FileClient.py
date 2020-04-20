from config import config


class FileClient:
    def __init__(self):
        self.fileHandle = None

    def sendMessage(self, message, isBinary):
        if self.fileHandle is None:
            self.fileHandle = open(config.get("player.name") + ".txt", "w")
        self.fileHandle.write(message + "\n")

    def checkNetworkClose(self):
        return None

    def stop(self):
        pass

    def join(self):
        pass


def CreateClient(url, port):
    return FileClient()
