from nestris_ocr.config import config  # TODO: remove this dependency.
from nestris_ocr.network.bytestuffer import prePackField

# Todo: numba optimize for numTiles
# Make sure we account for rotating piece above field, as this reduces
# Blockcount by 2
class FieldState(object):  # noqa: E302
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

    # todo: where does this belong?
    # in the net code?
    def serialize(self):
        result = self.data
        if config["network.protocol"] == "AUTOBAHN_V2":
            result = prePackField(result)
            result = result.tobytes()
        else:
            result2 = []
            for y in range(20):
                temp = "".join(str(result[y, x]) for x in range(10))
                result2.append(temp)
            result = "".join(str(r) for r in result2)
        return result
