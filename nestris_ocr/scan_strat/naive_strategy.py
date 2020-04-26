from nestris_ocr.scan_strat.base_strategy import BaseStrategy, GameState
from nestris_ocr.ocr_state.field_state import FieldState
from nestris_ocr.config import config

from nestris_ocr.scan_strat.scan_helpers import (
    scan_full,
    scan_level,
    scan_score,
    scan_lines,
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
        # compulsory tasks
        tasks.append(self.scan_score)
        tasks.append(self.scan_lines)
        tasks.append(self.scan_level)

        if config["calibration.capture_field"]:
            # if capture_field_method == 'LOOKUP': #yobi9 method
            #    tasks.append(self.scan_field_lookup)
            # else:
            tasks.append(self.scan_field_dynamic)
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
        img = scan_full(self.current_frame)
        for task in self.tasks:
            task(img)

    def scan_score(self, img):
        self.score = scan_score(img, "OOOOOO")

    def scan_lines(self, img):
        self.lines = scan_lines(img, "OOO")

    def scan_level(self, img):
        self.level = scan_level(img)

    def scan_field_dynamic(self, img):
        field_result = scan_field(img)
        self.field = FieldState(field_result["field"])
        self.color1 = field_result["color1"]
        self.color2 = field_result["color2"]

    def scan_field_lookup(self, img):
        pass
        # color1,color2 = lookup_colors(self.level)
        # scan_field(img, color1, color2)

    def scan_preview(self, img):
        self.preview = scan_preview(img)

    def scan_spawn(self, img):
        piece = scan_spawn(img)
        self.piece_stats.update(piece, self.current_time)

    def scan_stats_text(self, img):
        pass
        # pieces = scan_stats_text(img)
        # self.piece_stats.rewrite(pieces)
