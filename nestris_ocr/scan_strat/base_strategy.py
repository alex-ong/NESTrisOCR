import json
from enum import Enum
from nestris_ocr.config import config
from nestris_ocr.colors import Colors
from nestris_ocr.ocr_state.piece_stats import PieceStatAccumulator


class GameState(Enum):
    MENU = 1
    IN_GAME = 2


"""
Abstract base class.
Should write to lines,score,level etc
"""


def dict_zfill(item, digits):
    if item is not None:
        return str(item).zfill(digits)
    return None


class BaseStrategy(object):
    def __init__(self):
        self.lines = None
        self.score = None
        self.level = None
        self.start_level = None
        self.field = None
        self.preview = None
        self.gameid = 0
        self.piece_stats = PieceStatAccumulator()
        self.gamestate = GameState.MENU
        self.cur_piece = None
        self.cur_piece_das = None
        self.instant_das = None
        self.current_time = 0
        self.line_clear_anim = None
        self.colors = Colors()

        # initialize palette
        palette_name = config["calibration.palette"]

        try:
            with open("nestris_ocr/palettes/%s.json" % (palette_name,), "r") as file:
                palette = json.load(file)
                self.colors.setPalette(palette)

        except ValueError:
            print("Warning: Unable to load palette %s" % (palette_name,))

    # todo: don't include items not included in config.
    def to_dict(self):
        result = {}
        result["lines"] = dict_zfill(self.lines, 3)
        result["score"] = dict_zfill(self.score, 6)
        result["level"] = dict_zfill(self.level, 2)
        if config["calibration.capture_field"]:
            result["field"] = self.field
        if config["calibration.capture_preview"]:
            result["preview"] = self.preview
        result["gameid"] = self.gameid
        if config["stats.enabled"]:
            result.update(self.piece_stats.toDict())
        if config["calibration.capture_das"]:
            result["cur_piece"] = self.cur_piece
            result["cur_piece_das"] = self.cur_piece_das
            result["instant_das"] = self.instant_das
        if config["calibration.capture_line_clear"]:
            result["line_clear"] = self.line_clear_anim

        return result

    def update(self, timestamp, frame):
        self.current_time = timestamp
        self.current_frame = frame
        if self.gamestate == GameState.MENU:
            is_newgame = self.update_menu()
            if is_newgame:
                self.on_newgame()
        else:
            self.update_ingame()

    def update_menu(self):
        # returns whether we started a new game
        raise NotImplementedError("This is an abstract class, silly")

    def update_ingame(self):
        raise NotImplementedError("This is an abstract class, silly")

    def on_newgame(self):
        self.gameid += 1
