from threading import Lock

from nestris_ocr.ocr_state.piece_enum import Piece


# thread safe OCR status.
class PieceStatAccumulator(object):
    # min time between two pieces
    # since ARE = 10 frames, we can safely set it to 10 * 1/60
    TIME_EPSILON = 0.160  # min time between two pieces

    def __init__(self):
        self.lock = Lock()
        self.lastPieceTimeStamp = 0.0
        self.lastPiece = Piece.EMPTY
        self.T = 0
        self.J = 0
        self.Z = 0
        self.O = 0  # noqa: E741
        self.S = 0
        self.L = 0
        self.I = 0  # noqa: E741
        self._piece_count = 0

    def piece_count(self):
        return self._piece_count

    def meetsEpsilon(self, timeStamp):
        return timeStamp > self.lastPieceTimeStamp + self.TIME_EPSILON

    def reset(self):
        self.lock.acquire()
        self.T = 0
        self.J = 0
        self.Z = 0
        self.O = 0  # noqa: E741
        self.S = 0
        self.L = 0
        self.I = 0  # noqa: E741
        self._piece_count = 0
        self.lastPiece = Piece.EMPTY
        self.lock.release()

    def updatePiece(self, newPiece):
        if newPiece == Piece.T:
            self.T += 1
        elif newPiece == Piece.J:
            self.J += 1
        elif newPiece == Piece.Z:
            self.Z += 1
        elif newPiece == Piece.O:
            self.O += 1  # noqa: E741
        elif newPiece == Piece.S:
            self.S += 1
        elif newPiece == Piece.L:
            self.L += 1
        elif newPiece == Piece.I:
            self.I += 1  # noqa: E741
        self._piece_count += 1

    # used for naive implementation
    def rewrite(self, pieces):
        self.lock.acquire()
        self.T, self.J, self.Z, self.O, self.S, self.L, self.I = pieces  # noqa: E741
        self.lock.release()

    # returns if a new piece spawned
    def update(self, newPiece, timeStamp):
        if newPiece == Piece.UNKNOWN:
            return False

        self.lock.acquire()
        if newPiece == self.lastPiece:
            self.lock.release()
            return False

        result = False
        if (
            self.lastPiece == Piece.EMPTY
            and newPiece != Piece.EMPTY
            and self.meetsEpsilon(timeStamp)
        ):
            self.updatePiece(newPiece)
            self.lastPieceTimeStamp = timeStamp
            result = True

        self.lastPiece = newPiece
        self.lock.release()
        return result

    def toDict(self):
        self.lock.acquire()
        result = {
            "T": str(self.T).zfill(3),
            "J": str(self.J).zfill(3),
            "Z": str(self.Z).zfill(3),
            "O": str(self.O).zfill(3),
            "S": str(self.S).zfill(3),
            "L": str(self.L).zfill(3),
            "I": str(self.I).zfill(3),
        }
        self.lock.release()
        return result
