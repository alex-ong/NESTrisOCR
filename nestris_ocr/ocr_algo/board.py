from PIL import Image
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
def parseImage(img, colors):
    img = img.resize((10, 20), Image.NEAREST)
    img = np.array(img, dtype=np.uint8)

    return parseImage2(img, colors.black, colors.white, colors.color1, colors.color2)


if __name__ == "__main__":
    # run this from root directory as "python -m nestris_ocr.ocr_algo.board"
    from nestris_ocr.colors import Colors

    img = Image.open("nestris_ocr/assets/test/board_lvl7.png")

    colors = Colors()
    colors.setLevel(7)

    t = time.time()
    for i in range(100):
        parseImage(img, colors)
    print(time.time() - t)

    print(parseImage(img, colors))
