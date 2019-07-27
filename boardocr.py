import PIL
from enum import Enum

class Piece(Enum):
    T = 0
    J = 1
    Z = 2
    O = 3
    S = 4
    L = 5
    I = 6
    EMPTY = 7
    
class OCRStatus(object):
    def __init__(self):
        self.lastPiece = Piece.EMPTY
        self.T = 0
        self.J = 0
        self.Z = 0
        self.O = 0
        self.S = 0
        self.L = 0
        self.I = 0
        
    def reset(self):
        self.T = 0
        self.J = 0
        self.Z = 0
        self.O = 0
        self.S = 0
        self.L = 0
        self.I = 0

    def update(self, newPiece):
        if self.lastPiece == Piece.EMPTY and newPiece != Piece.EMPTY:
            if newPiece == Piece.T:
                self.T += 1
            elif newPiece == Piece.J:
                self.J += 1
            elif newPiece == Piece.Z:
                self.Z += 1
            elif newPiece == Piece.O:
                self.O += 1
            elif newPiece == Piece.S:
                self.S += 1
            elif newPiece == Piece.L:
                self.L += 1
            elif newPiece == Piece.I:
                self.I += 1
        self.lastPiece = newPiece
    
    def toDict(self):
        return { "T": str(self.T),
                 "J": str(self.J),
                 "Z": str(self.Z),
                 "O": str(self.O),
                 "S": str(self.S),
                 "L": str(self.L),
                 "I": str(self.I)
               }