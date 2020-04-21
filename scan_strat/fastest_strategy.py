from scan_strat.base_strategy import GameState, BaseStrategy
from ocr_state.field_state import FieldState
from FullStateOptimizer.FullStateConfiguration import FS_CONFIG
from ocr_state.level_transition import get_level
from scan_strat.scan_helpers import (
    scan_full,
    scan_level,
    scan_score,
    scan_lines,
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
        img = scan_full(self.hwnd)
        lines = scan_lines(img, "OOO")
        score = scan_score(img, "OOOOOO")
        level = scan_level(img)

        if lines and score and level:
            if lines == "000" and score == "000000":
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
        img = scan_full(self.hwnd)
        piece_spawned = False
        soft_drop_updated = False  # check softdrop once per frame.

        lines_cleared = self.get_lines_cleared(img)

        if lines_cleared is None:  # possibly menu
            self.gamestate = GameState.MENU
            return

        if lines_cleared > 0:
            self.lines += lines_cleared
            new_level = get_level(self.lines, self.start_level)
            if self.level != new_level:
                self.level = new_level
                self.color1 = None
                self.color2 = None
            self.score += self.get_score(lines_cleared)
            self.update_softdrop(img)
            soft_drop_updated = True

        if FS_CONFIG.capture_field:
            field_info = scan_field(img, self.color1, self.color2)
            field = FieldState(field_info["field"])
            if field == self.field:
                return
            if field.piece_spawned(self.field):
                piece_spawned = True
            if field.line_clear_animation(self.field):
                pass  # todo pass flashing / etc
            self.field = field

        if FS_CONFIG.capture_stats and FS_CONFIG.stats_method == "FIELD":
            spawned = scan_spawn(img)
            did_spawn = self.piece_stats.update(spawned, self.current_time)
            piece_spawned = piece_spawned or did_spawn
        elif FS_CONFIG.capture_stats and FS_CONFIG.stats_method == "TEXT":
            counts = scan_stats_text(img)
            if sum(counts) > self.piece_stats.piece_count():
                self.piece_stats.rewrite(counts)
                piece_spawned = True

        # check softdrop only on piece spawn
        if piece_spawned:
            if FS_CONFIG.capture_preview:
                self.preview = self.get_next_piece(img)
            if not soft_drop_updated:
                success = self.update_softdrop(img)
                if not success:
                    pass
        # check softdrop on every frame, if we're not detecting piece spawns.
        elif not FS_CONFIG.capture_field and not FS_CONFIG.capture_stats:
            if not soft_drop_updated:
                success = self.update_softdrop(img)
                if not success:
                    pass

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
        return scan_preview(img)

    # a forced refresh.
    def update_ingame_full(self):
        pass
