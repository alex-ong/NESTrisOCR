from PIL import Image
import numpy as np


try:
    from nestris_ocr.ocr_algo.board_ocr import ao9_parse, shine_parse, color_dist
except (ModuleNotFoundError, ImportError):
    from nestris_ocr.ocr_algo.board2 import ao9_parse, shine_parse, color_dist

    print("dev: Using board_ocr via llvmlite")
    # Run build_fastboard.py to create an AOT version.
    # the llvmlite version is actually faster.

# when color difference between black and color1/color2 is under this threshold,
# use Shine detection as well as ao9
SHINE_THRESHOLD = 2000

# expecting all 4 colors as np.array(dtype=np.uint8)


def parseImage(img, colors):
    dist1 = color_dist(colors.black, colors.color1)
    dist2 = color_dist(colors.black, colors.color2)

    if dist1 < SHINE_THRESHOLD or dist2 < SHINE_THRESHOLD:
        img = img.resize((80, 160))
        img = np.array(img, dtype=np.uint8)

        bw = np.stack([colors.black, colors.white])
        no_b = np.stack([colors.white, colors.color1, colors.color2])
        result = shine_parse(img, bw, no_b)

        return result

    img = np.array(img, dtype=np.uint8)

    return ao9_parse(
        img, np.stack([colors.black, colors.white, colors.color1, colors.color2])
    )


if __name__ == "__main__":
    # run this from root directory as "python -m nestris_ocr.ocr_algo.board"
    from nestris_ocr.colors import Colors
    import nestris_ocr.utils.time as time

    img = Image.open("nestris_ocr/assets/test/board_lvl7.png")

    colors = Colors()
    colors.setLevel(7)

    iterations = 25000

    start = time.time()
    for i in range(iterations):
        parseImage(img, colors)

    elapsed = time.time() - start
    print(elapsed, elapsed / iterations)

    print(parseImage(img, colors))
