from enum import Enum
from FullStateOptimizer.FullStateConfiguration import FS_CONFIG
from FullStateOptimizer.OCRHelpers import (
scan_full,
scan_level,   
scan_score,
scan_lines,
scan_field,
scan_preview,
scan_spawn
)
from FullStateOptimizer.Transition import TRANSITION
from OCRAlgo.PieceStatsBoardOCR import PieceStatAccumulator
import time

def clamp(my_value, min_value, max_value):
    return max(min(my_value, max_value), min_value)

class GameState(Enum):
    MENU = 1
    IN_GAME = 2
        
        
class FullStateOCR(object):
    def __init__(self, hwnd):
        self.lines = None
        self.score = None
        self.level = None
        self.start_level = None
        self.field = None
        self.preview = None
        self.color1 = None
        self.color2 = None
        self.gameid = 0
        self.piece_stats = PieceStatAccumulator()
        self.gamestate = GameState.MENU
        self.hwnd = hwnd

    def update(self):
        if self.gamestate == GameState.MENU:
            self.update_menu()
        else:
            self.update_ingame()

    # simply tries to get into game
    def update_menu(self):
        img = scan_full(self.hwnd)
        lines = scan_lines(img, 'OOO')
        score = scan_score(img, 'OOOOOO')
        level = scan_level(img)
        
        if lines and score and level:
            if lines == '000' and score == '000000':
                self.level = int(level)
                self.start_level = self.level
                self.gamestate = GameState.IN_GAME
                self.field = None
                self.gameid += 1
                self.piece_stats.reset()
            elif lines == self.lines:
                self.gamestate = GameState.IN_GAME
                #requireFullRefresh = True
                
    
    def update_ingame(self):
        timestamp = time.time()
        img = scan_full(self, hwnd)
        piece_spawned = False
        line_cleared = False
        soft_drop_points = 0
        full_required = False

        if FS_CONFIG.capture_field:
            field_info = scan_field(img,self.color1,self.color2)
            field = FieldState(field_info['field'])
            c1 = field_info['color1']
            c2 = field_info['color2']
            if field == self.field:
                return
            if field.piece_spawned(self.field):
                piece_spawned = True
            if field.line_clear_animation(self.field):
                pass #todo pass flashing / etc
            self.field = field

        if FS_CONFIG.capture_stats and FS_CONFIG.stats_method == 'FIELD':
            spawned = scan_spawn(img)
            did_spawn = self.piece_stats.update(spawned, timestamp)
            piece_spawned = piece_spawned or did_spawn
        
        if piece_spawned:
            lines_cleared = self.get_lines_cleared()
            self.preview = self.get_next_piece()

            if lines_cleared and lines_cleared > 0:
                self.lines += lines_cleared
                self.level = self.get_level(this.lines)
                self.score += self.get_score(lines_cleared)
                
            softdrop = self.get_soft_drop(img)
            self.score += softdrop
    
    def get_level(self):
        low = self.start_level
        transition = TRANSITION[self.start_level]
        lines = max(lines-transition,0)
        result = lines // 10 + self.start_level
        return result

    def get_score(self, lines_cleared):
        lookup = [40,100,300,1200]
        return (self.level + 1) * lookup[lines_cleared]
    
    def get_soft_drop(self, img):
        # check for score capping.
        if self.score >= 999999:
            digits = scan_score(img, 'OOOOOO')
            if digits and digits == '999999':
                return 0
        else: #fast scan.
            digits = scan_score(img, 'XXXXOO')

        if digits is None:
            return None

        digits = int(digits[4:])
        diff = digits - self.score % 100
        if diff < 100:
            diff += 100
        return diff

    def get_lines_cleared(self):
        line_digits = scan_lines(img, 'XXO')
        if line_digits is None:
            return None

        last_digit = int(line_digit[2])
        cleared = last_digit - self.lines % 10
        
        if cleared < 0:
            cleared += 10
        
        return cleared

    # a forced refresh.
    def update_ingame_full(self):
        pass

# Todo: numba optimize for numTiles
# Make sure we account for rotating piece above field, as this reduces
# Blockcount by 2
class FieldState(object):
    def __init__(self, data):
        self.data = data

    # returns block count for field below row 18
    def blockCountAdjusted(self):
        return 0
