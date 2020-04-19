import PIL
from enum import Enum
from threading import Lock
from ocr_state.piece_enum import Piece


def isBlack(colour):
    limit = 20
    return colour[0] < limit and colour[1] < limit and colour[2] < limit


def parseImage(img):
    img = img.resize((4, 2), PIL.Image.NEAREST)
    img = img.load()
    r = not isBlack(img[3, 1])
    g = not isBlack(img[3, 0])
    b = not isBlack(img[2, 1])
    o = not isBlack(img[1, 1])

    k1 = isBlack(img[0, 0])
    k2 = isBlack(img[1, 0])
    k3 = isBlack(img[2, 0])
    k4 = isBlack(img[0, 1])

    k = k1 and k2 and k3 and k4  # are all the other 4 tiles black?

    result = patternToPiece(r, g, b, o, k)
    return result


#  pattern
# ...xxxg...
# ....obr...
# ..........
# look at boardOCR doc.


def patternToPiece(r, g, b, o, k):
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
