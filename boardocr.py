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
    UNKNOWN = 8
    
def isBlack(colour):
    limit = 20
    return (colour[0] < limit and
           colour[1] < limit and
           colour[2] < limit)
           

def parseImage(img):   
    img = img.resize((4,2),PIL.Image.NEAREST)
    img = img.load()
    r = not isBlack(img[3,1])
    g = not isBlack(img[3,0])
    b = not isBlack(img[2,1])
    o = not isBlack(img[1,1])
    
    k1 = isBlack(img[0,0])
    k2 = isBlack(img[1,0])
    k3 = isBlack(img[2,0])
    k4 = isBlack(img[0,1])
    
    k = k1 and k2 and k3 and k4 #are all the other 4 tiles black?
    
    result = patternToPiece(r,g,b,o, k)
            
    return result
    
#  pattern
#...xxxg...
#....obr...
#..........
# look at boardOCR doc.

def patternToPiece(r,g,b,o,k):    
    if g and not o and not b and not r:
        return Piece.I
    if not g and o and b and not r:
        return Piece.O
    if g and not o and b and not r:
        return Piece.T
    if g and o and not b and not r:
        return Piece.L
    if g and not o and not b and r:
        return Piece.J
    if g and o and b and not r:
        return Piece.S
    if not g and not o and b and r:
        return Piece.Z
        
    if not g and not o and not b and not r and k:
        return Piece.EMPTY
    else:
        return Piece.UNKNOWN
        


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
        self.lastPiece = Piece.EMPTY

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
        
        if newPiece != Piece.UNKNOWN:
            self.lastPiece = newPiece
    
    def toDict(self):
        return { 
                 "T": str(self.T).zfill(3),
                 "J": str(self.J).zfill(3),
                 "Z": str(self.Z).zfill(3),
                 "O": str(self.O).zfill(3),
                 "S": str(self.S).zfill(3),
                 "L": str(self.L).zfill(3),
                 "I": str(self.I).zfill(3)
               }
               
        