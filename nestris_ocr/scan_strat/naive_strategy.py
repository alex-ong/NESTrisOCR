from nestris_ocr.scan_strat.base_strategy import BaseStrategy, GameState
from nestris_ocr.ocr_state.field_state import FieldState
from nestris_ocr.config import config

from nestris_ocr.scan_strat.scan_helpers import (
    scan_full,
    scan_black_n_white,
    scan_level,
    scan_score,
    scan_lines,
    scan_colors,
    lookup_colors,
    scan_field,
    scan_preview,
    scan_spawn,
)

# from FullStateOptimizer.Transition import TRANSITION

# import time


class NaiveStrategy(BaseStrategy):
    def __init__(self, *args):
        super(NaiveStrategy, self).__init__(*args)
        self.tasks = self.setup_tasks()

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
            if config["calibration.dynamic_color"]:
                tasks.append(self.scan_colors)
            elif config["calibration.color_interpolation"]:
                tasks.append(self.lookup_colors_w_interpolation)
            else:
                tasks.append(self.lookup_colors)

            tasks.append(self.scan_field)

        if config["calibration.capture_preview"]:
            tasks.append(self.scan_preview)
        if config["stats.enabled"]:
            if config["stats.capture_method"] == "FIELD":
                tasks.append(self.scan_spawn)
            elif config["stats.capture_method"] == "TEXT":
                tasks.append(self.scan_stats_text)
        return tasks

    # Naive strategy does not care about gamestate
    def update_menu(self):
        self.gamestate = GameState.IN_GAME

    def update_ingame(self):
        for task in self.tasks:
            task(self.current_frame)

    def scan_black_n_white(self, img):
        result = scan_black_n_white(img)
        self.black = result["black"]
        self.white = result["white"]

    def scan_colors(self, img):
        result = scan_colors(img)
        self.color1 = result["color1"]
        self.color2 = result["color2"]

    def lookup_colors_w_interpolation(self):
        result = lookup_colors(self.level, self.black["rgb"], self.white["rgb"])
        self.color1 = result["color1"]
        self.color2 = result["color2"]

    def lookup_colors(self):
        result = lookup_colors(self.level)
        self.color1 = result["color1"]
        self.color2 = result["color2"]

    def scan_score(self, img):
        self.score = scan_score(img, "OOOOOO")

    def scan_lines(self, img):
        self.lines = scan_lines(img, "OOO")

    def scan_level(self, img):
        self.level = scan_level(img)

    def scan_field(self, img):
        result = scan_field(img, self.black, self.white, self.color1, self.color2)
        self.field = FieldState(result)

    def scan_preview(self, img):
        self.preview = scan_preview(img)

    def scan_spawn(self, img):
        piece = scan_spawn(img)
        self.piece_stats.update(piece, self.current_time)

    def scan_stats_text(self, img):
        pass
        # pieces = scan_stats_text(img)
        # self.piece_stats.rewrite(pieces)
