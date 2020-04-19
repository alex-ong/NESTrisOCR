from enum import Enum
from ocr_state.piece_stats import PieceStatAccumulator


class GameState(Enum):
    MENU = 1
    IN_GAME = 2


"""
Abstract base class.
Should write to lines,score,level etc
"""


class BaseStrategy(object):
    def __init__(self, hwnd):
        self.lines = None
        self.score = None
        self.level = None
        self.start_level = None
        self.field = None
        self.preview = None
        self.color1 = None  # cached color1
        self.color2 = None  # cached color2
        self.gameid = 0
        self.piece_stats = PieceStatAccumulator()
        self.gamestate = GameState.MENU
        self.das_counter = 0
        self.hwnd = hwnd

    def to_dict_menu(self):
        result = {}
        result["lines"] = None
        result["score"] = None
        result["level"] = None
        result["field"] = None
        result["preview"] = None
        result["gameid"] = None
        result.update(self.piece_stats.toDict())
        return result

    def to_dict(self):
        if self.gamestate == GameState.MENU:
            return self.to_dict_menu()
        result = {}
        result["lines"] = str(self.lines).zfill(3)
        result["score"] = str(self.score).zfill(6)
        result["level"] = str(self.level).zfill(2)
        result["field"] = None
        result["preview"] = None
        result["gameid"] = None
        result["das_counter"] = None
        result.update(self.piece_stats.toDict())
        return result

    def update(self):
        if self.gamestate == GameState.MENU:
            self.update_menu()
        else:
            self.update_ingame()

    def update_menu(self):
        raise NotImplementedError("This is an abstract class, silly")

    def update_ingame(self):
        raise NotImplementedError("This is an abstract class, silly")
