import numpy as np
from nestris_ocr.config import config  # TODO: remove this dependency.
from nestris_ocr.network.byte_stuffer import prePackField

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
            result = np.array_equal(self.data, other.data)
            return result

        return False

    # In Python3, don't implement __ne__
    # def __ne__(self, other):
    #   ...

    def piece_spawned(self, other):
        return False

    def line_clear_animation(self, other):
        return False

    # todo: where does this belong?
    # in the net code?
    def serialize(self):
        result = self.data
        if config["network.protocol"] in ["AUTOBAHN_V2", "AUTOBAHN_SERVER"]:
            result = prePackField(result)
            result = result.tobytes()
        else:
            return self.simple_string()
        return result

    def simple_string(self):
        one_d = self.data.flatten()
        result = "".join(str(r) for r in one_d)
        return result

    def __str__(self):
        return self.simple_string()
