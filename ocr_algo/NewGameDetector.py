class NewGameDetector:
    def __init__(self):
        self.score = None
        self.lines = None
        self.level = None
        self.gameId = 0

    # we only consider transitioning from all null to all '0' and vice versa.
    def getGameID(self, score, lines, level):
        changed = False
        if self.score is None and self.lines is None and self.level is None:
            if score == "000000" and lines == "000":
                self.gameId += 1
                self.score = score
                self.lines = lines
                self.level = level
                changed = True
        elif score is None and lines is None and level is None:
            self.score = score
            self.lines = lines
            self.level = level

        return self.gameId, changed
