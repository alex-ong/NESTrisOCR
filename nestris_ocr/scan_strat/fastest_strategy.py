from nestris_ocr.scan_strat.base_strategy import GameState, BaseStrategy
from nestris_ocr.ocr_state.field_state import FieldState
from nestris_ocr.full_state_optimizer.full_state_config import FS_CONFIG
from nestris_ocr.ocr_state.level_transition import get_level
from nestris_ocr.config import config

from nestris_ocr.scan_strat.scan_helpers import (
    scan_black_n_white,
    scan_level,
    scan_score,
    scan_lines,
    scan_colors,
    lookup_colors,
    scan_field,
    scan_preview,
    scan_spawn,
    scan_stats_text,
)


def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)


class FastestStrategy(BaseStrategy):

    # simply tries to get into game
    def update_menu(self):
        # use default black and white on start
        lines = scan_lines(self.current_frame, "OOO")
        score = scan_score(self.current_frame, "OOOOOO")
        level = scan_level(self.current_frame)

        if lines and score and level:
            if lines == "000" and score == "000000":
                if config["calibration.dynamic_black_n_white"]:
                    # read once per game
                    result = scan_black_n_white(self.current_frame)
                    self.black = result["black"]
                    self.white = result["white"]

                self.get_colors(self.current_frame)
                self.level = int(level)
                self.lines = 0
                self.score = 0
                self.start_level = self.level
                self.gamestate = GameState.IN_GAME
                self.field = None
                self.gameid += 1
                self.piece_stats.reset()
                print("moved from menu to game")
            elif int(lines) == self.lines:
                self.gamestate = GameState.IN_GAME
                # requireFullRefresh = True

    def update_ingame(self):
        piece_spawned = False
        soft_drop_updated = False  # check softdrop once per frame.

        lines_cleared = self.get_lines_cleared(self.current_frame)

        if lines_cleared is None:  # possibly menu
            self.gamestate = GameState.MENU
            return

        if lines_cleared > 0:
            self.lines += lines_cleared
            new_level = get_level(self.lines, self.start_level)
            if self.level != new_level:
                self.level = new_level
                self.get_colors(self.current_frame)
            self.score += self.get_score(lines_cleared)
            self.update_softdrop(self.current_frame)
            soft_drop_updated = True

        if FS_CONFIG.capture_field:
            field_data = scan_field(
                self.current_frame,
                self.black["rgb"],
                self.white["rgb"],
                self.color1,
                self.color2,
            )
            field = FieldState(field_data)
            if field == self.field:
                return
            if field.piece_spawned(self.field):
                piece_spawned = True
            if field.line_clear_animation(self.field):
                pass  # todo pass flashing / etc
            self.field = field

        if FS_CONFIG.capture_stats and FS_CONFIG.stats_method == "FIELD":
            spawned = scan_spawn(self.current_frame)
            did_spawn = self.piece_stats.update(spawned, self.current_time)
            piece_spawned = piece_spawned or did_spawn
        elif FS_CONFIG.capture_stats and FS_CONFIG.stats_method == "TEXT":
            counts = scan_stats_text(self.current_frame)
            if sum(counts) > self.piece_stats.piece_count():
                self.piece_stats.rewrite(counts)
                piece_spawned = True

        # check softdrop only on piece spawn
        if piece_spawned:
            if FS_CONFIG.capture_preview:
                self.preview = self.get_next_piece(self.current_frame)
            if not soft_drop_updated:
                success = self.update_softdrop(self.current_frame)
                if not success:
                    pass
        # check softdrop on every frame, if we're not detecting piece spawns.
        elif not FS_CONFIG.capture_field and not FS_CONFIG.capture_stats:
            if not soft_drop_updated:
                success = self.update_softdrop(self.current_frame)
                if not success:
                    pass

    def get_colors(self, img):
        if config["calibration.dynamic_color"]:
            result = scan_colors(img)
        elif config["calibration.color_interpolation"]:
            result = lookup_colors(
                self.levelInt(), self.black["rgb"], self.white["rgb"]
            )
        else:
            result = lookup_colors(self.levelInt())

        self.color1 = result["color1"]
        self.color2 = result["color2"]

    def update_softdrop(self, img):
        softdrop = self.get_soft_drop(img)
        if softdrop:
            self.score += softdrop
        return softdrop

    def get_score(self, lines_cleared):
        print(lines_cleared)
        lookup = [0, 40, 100, 300, 1200]
        return (self.level + 1) * lookup[lines_cleared]

    def get_soft_drop(self, img):
        # check for score capping.
        if self.score >= 999999:
            # todo: cache whether cart supports ENEOOGEZ
            digits = scan_score(img, "OOOOOO")
            if digits and digits == "999999":
                return 0
        else:  # fast scan.
            digits = scan_score(img, "XXXXOO")

        if digits is None:
            return None

        digits = int(digits[4:])
        diff = digits - self.score % 100
        if diff < 0:
            diff += 100
        return diff

    def get_lines_cleared(self, img):
        line_digits = scan_lines(img, "XXO")
        if line_digits is None:
            return None

        last_digit = int(line_digits[2])
        cleared = last_digit - self.lines % 10

        if cleared < 0:
            cleared += 10

        # if cleared != 0:
        #    img.save("last-line-clear.png")

        return cleared

    def get_next_piece(self, img):
        return scan_preview(img, self.black["luma"])

    # a forced refresh.
    def update_ingame_full(self):
        pass
