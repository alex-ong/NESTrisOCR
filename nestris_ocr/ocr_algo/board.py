import PIL
import numpy as np
import time

from nestris_ocr.config import config
from nestris_ocr.network.byte_stuffer import prePackField

try:
    from nestris_ocr.ocr_algo.board_ocr import parseImage2  # if it's built
except ImportError:
    from nestris_ocr.ocr_algo.board2 import parseImage2

    print(
        "Warning, loaded parseImage2 from llvmlite: please run buildBoardOCR2 to build a compiled version"
    )


def parseImage(img, color1, color2, pre_calculated=False):
    if not pre_calculated:
        color1 = color1.resize((1, 1), PIL.Image.ANTIALIAS)
        color1 = color1.getpixel((0, 0))
        color1 = np.array(color1, dtype=np.uint8)
        color2 = color2.resize((1, 1), PIL.Image.ANTIALIAS)
        color2 = color2.getpixel((0, 0))
        color2 = np.array(color2, dtype=np.uint8)

    img = img.resize((10, 20), PIL.Image.NEAREST)
    img = np.array(img, dtype=np.uint8)

    black = (10, 10, 10)
    white = (240, 240, 240)

    black = np.array(black, dtype=np.uint8)
    white = np.array(white, dtype=np.uint8)

    result = {}
    result["field"] = parseImage2(img, black, white, color1, color2)
    result["color1"] = color1
    result["color2"] = color2
    return result


# run as python -m ocr_algo.board
if __name__ == "__main__":

    from PIL import Image

    img = Image.open("assets/test/board.jpg")
    color1 = Image.open("assets/test/color1.jpg")
    color2 = Image.open("assets/test/color2.jpg")
    t = time.time()
    for i in range(100):
        parseImage(img, color1, color2)
    print(time.time() - t)
