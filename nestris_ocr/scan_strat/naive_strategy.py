from nestris_ocr.scan_strat.base_strategy import BaseStrategy, GameState
from nestris_ocr.ocr_state.field_state import FieldState
from nestris_ocr.config import config
from nestris_ocr.ocr_algo.line_clear import LineClearDetection

from nestris_ocr.scan_strat.scan_helpers import (
    scan_black_n_white,
    scan_level,
    scan_score,
    scan_lines,
    scan_colors,
    scan_field,
    scan_preview,
    scan_spawn,
    scan_das_current_piece,
    scan_das_current_piece_das,
    scan_das_instant_das,
    scan_stats_text,
)

# from FullStateOptimizer.Transition import TRANSITION

# import time


class NaiveStrategy(BaseStrategy):
    def __init__(self, *args):
        super(NaiveStrategy, self).__init__(*args)
        self.gamestate = GameState.IN_GAME  # allows starting OCR mid-game
        self.tasks = self.setup_tasks()
        self.interpolate = config["calibration.color_interpolation"]

    def on_newgame(self):
        super().on_newgame()
        if config["calibration.capture_line_clear"]:
            self.line_clear_detect.reset()

    # sets up the tasks that we will be doing naively.
    def setup_tasks(self):
        tasks = []

        if config["calibration.dynamic_black_n_white"]:
            tasks.append(self.scan_black_n_white)

        # compulsory tasks
        tasks.append(self.scan_score)
        tasks.append(self.scan_lines)
        tasks.append(self.scan_level)

        if config["calibration.capture_field"]:
            if config["calibration.dynamic_colors"]:
                tasks.append(self.scan_colors)
            else:
                tasks.append(self.lookup_colors)

            tasks.append(self.scan_field)
            if config["calibration.capture_line_clear"]:
                self.line_clear_detect = LineClearDetection()

        if config["calibration.capture_preview"]:
            tasks.append(self.scan_preview)

        if config["stats.enabled"]:
            if config["stats.capture_method"] == "FIELD":
                tasks.append(self.scan_spawn)
            elif config["stats.capture_method"] == "TEXT":
                tasks.append(self.scan_stats_text)

        if config["calibration.capture_das"]:
            tasks.append(self.scan_das_current_piece)
            tasks.append(self.scan_das_current_piece_das)
            tasks.append(self.scan_das_instant_das)

        return tasks

    def to_dict(self):
        result = super(NaiveStrategy, self).to_dict()
        return result

    # Naive strategy does not care about gamestate
    def update_menu(self):
        for task in self.tasks:
            task(self.current_frame)

        if self.lines and self.score and self.level:
            self.gamestate = GameState.IN_GAME
            if (self.lines == "000" or self.lines == "025") and self.score == "000000":
                return True

        return False

    def update_ingame(self):
        for task in self.tasks:
            task(self.current_frame)

        if not self.lines:
            self.gamestate = GameState.MENU

    def scan_black_n_white(self, img):
        result = scan_black_n_white(img)
        self.colors.setBlackWhite(*result)

    def scan_colors(self, img):
        result = scan_colors(img)
        self.colors.setColor1Color2(*result)

    def levelInt(self):
        try:
            # TODO parse levels 30+ and their weird hex rendering
            return int(self.level)
        except ValueError:
            return 0
        except TypeError:
            return 0

    def lookup_colors(self, img):
        self.colors.setLevel(self.levelInt(), self.interpolate)

    def scan_score(self, img):
        self.score = scan_score(img, "OOOOOO")

    def scan_lines(self, img):
        self.lines = scan_lines(img, "OOO")

    def scan_level(self, img):
        self.level = scan_level(img)

    def scan_field(self, img):
        result = scan_field(img, self.colors)
        self.field = FieldState(result)
        if config["calibration.capture_line_clear"]:
            self.line_clear_anim = self.line_clear_detect.process(self.field.data)

    def scan_preview(self, img):
        self.preview = scan_preview(img, self.colors)

    def scan_spawn(self, img):
        piece = scan_spawn(img, self.colors)
        self.piece_stats.update(piece, self.current_time)

    def scan_das_current_piece(self, img):
        self.cur_piece = scan_das_current_piece(img, self.colors)

    def scan_das_current_piece_das(self, img):
        self.cur_piece_das = scan_das_current_piece_das(img, "OO")

    def scan_das_instant_das(self, img):
        self.instant_das = scan_das_instant_das(img, "OO")

    def scan_stats_text(self, img):
        pieces = scan_stats_text(img)
        self.piece_stats.rewrite(pieces)
