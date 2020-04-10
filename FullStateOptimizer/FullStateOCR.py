from enum import Enum

class GameState(Enum):
    MENU = 1
    IN_GAME = 2
        
        
class FullStateOCR(object):
    def __init__ (self):
        self.lines = None
        self.score = None
        self.level = None
        self.field = None
        self.gamestate = GameState.MENU

    def update(self):
        if self.gamestate == GameState.MENU:
            self.update_menu()
        else:
            self.update_ingame()

    # simply checks for in-game, and 
    def update_menu(self):
                
    def update_ingame(self, force=False):
        
    # a forced refresh.            
    def update_ingame_full(self):
        pass

#todo: numba optimize for numTiles
#make sure we account for rotating piece above field, as this reduces blockcount by 2
class FieldState(object):
    def __init__(self, data):
        self.data = data

    # returns block count for field below row 18
    def blockCountAdjusted(self):
        return 0
