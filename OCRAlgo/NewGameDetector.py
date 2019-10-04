
class NewGameDetector():
    def __init__(self):
        self.score = None
        self.lines = None
        self.level = None
        self.gameId = 0
        
    def getGameID(self, score, lines,level):
        if (self.score == None and
            self.lines == None and
            self.level == None):
            if score == '000000' and lines == '000':
                self.gameId += 1
        self.score = score
        self.lines = lines
        self.level = level
        
        return self.gameId
            