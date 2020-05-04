import PIL
import numpy as np
import time

try:
    from nestris_ocr.ocr_algo.board_ocr import parseImage2  # if it's built
except ImportError:
    from nestris_ocr.ocr_algo.board2 import parseImage2

    print(
        "Warning, loaded parseImage2 from llvmlite: please run buildBoardOCR2 to build a compiled version"
    )


# expecting all 4 colors as np.array(dtype=np.uint8)
def parseImage(img, black, white, color1, color2):
    img = img.resize((10, 20), PIL.Image.NEAREST)
    img = np.array(img, dtype=np.uint8)

    return parseImage2(img, black, white, color1, color2)


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
