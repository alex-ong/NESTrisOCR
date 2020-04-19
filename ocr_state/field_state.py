# Todo: numba optimize for numTiles
# Make sure we account for rotating piece above field, as this reduces
# Blockcount by 2
class FieldState(object):
    def __init__(self, data):
        self.data = data

    # returns block count for field below row 18
    def blockCountAdjusted(self):
        return 0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return False
            # return self.__dict__ == other.__dict__

    def piece_spawned(self, other):
        return False

    def line_clear_animation(self, other):
        return False
