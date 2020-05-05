import PIL
from nestris_ocr.ocr_state.piece_enum import Piece


def isBlack(colour, black_luma):
    return colour[0] < black_luma and colour[1] < black_luma and colour[2] < black_luma


def parseImage(img, black_luma=10):
    img = img.resize((4, 2), PIL.Image.NEAREST)
    img = img.load()
    r = not isBlack(img[3, 1], black_luma)
    g = not isBlack(img[3, 0], black_luma)
    b = not isBlack(img[2, 1], black_luma)
    o = not isBlack(img[1, 1], black_luma)

    k1 = isBlack(img[0, 0], black_luma)
    k2 = isBlack(img[1, 0], black_luma)
    k3 = isBlack(img[2, 0], black_luma)
    k4 = isBlack(img[0, 1], black_luma)

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
