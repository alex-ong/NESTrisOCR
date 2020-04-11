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

from OCRAlgo.PieceStatsBoardOCR import PieceStatAccumulator
import time

class GameState(Enum):
    MENU = 1
    IN_GAME = 2
        
        
class FullStateOCR(object):
    def __init__(self, hwnd):
        self.lines = None
        self.score = None
        self.level = None
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
                self.gamestate = GameState.IN_GAME
                self.field = None
                self.gameid += 1
                self.piece_stats.reset()
                
    
    def update_ingame(self):
        timestamp = time.time()
        img = scan_full(self, hwnd)
        piece_spawned = False
        if FS_CONFIG.capture_field:
            field_info = scan_field(img,self.color1,self.color2)
            field = FieldState(field_info['field'])
            c1 = field_info['color1']
            c2 = field_info['color2']
            if field == self.field:
                return
            if field.piece_spawned(self.field):
                piece_spawned = True

        if FS_CONFIG.capture_stats and FS_CONFIG.stats_method == 'FIELD':
            spawned = scan_spawn(img)
            did_spawn = self.piece_stats.update(spawned, timestamp)
            piece_spawned = piece_spawned or did_spawn
            

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
