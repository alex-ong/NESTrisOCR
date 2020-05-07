from PIL import Image
from nestris_ocr.ocr_state.piece_enum import Piece


def parseImage(img, colors):
    img = img.resize((4, 2), Image.NEAREST)
    img = img.load()

    r = not colors.isBlack(img[3, 1])
    g = not colors.isBlack(img[3, 0])
    b = not colors.isBlack(img[2, 1])
    o = not colors.isBlack(img[1, 1])

    k1 = colors.isBlack(img[0, 0])
    k2 = colors.isBlack(img[1, 0])
    k3 = colors.isBlack(img[2, 0])
    k4 = colors.isBlack(img[0, 1])

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


if __name__ == "__main__":
    # run this from root directory as "python -m nestris_ocr.ocr_algo.piece_stats_spawn"
    img = Image.open("nestris_ocr/assets/test/spawn_z.png")
    import time
    from nestris_ocr.colors import Colors

    colors = Colors()

    iterations = 100000

    t = time.time()
    for i in range(iterations):
        parseImage(img, colors)
    print(time.time() - t, (time.time() - t) / iterations)
