﻿from PIL import Image, ImageEnhance
import numpy as np

cachedOffsets = []
cachedPPP = None

COUNT_PERC = 0.7

PreviewImageSize = (31, 15)


# look at assets/doc for description
def parseImage(img, colors):
    img = img.resize((31, 15), Image.BOX)
    img = ImageEnhance.Contrast(img).enhance(3.0)
    img = img.convert("L")
    img = img.getdata()
    img = np.asarray(img)
    # img is in y,x format
    img = np.reshape(img, (15, -1))

    black_luma = colors.black_luma

    img = np.vectorize(lambda pixel: 1 if pixel > black_luma else 0)(img)

    # first, check for I and None
    i_pixels = np.sum(img[4:11, :4]) + np.sum(img[4:11, -4:])  # perfect score is 56.
    i_pixels = i_pixels >= int(56 * COUNT_PERC)

    if i_pixels:
        return "I"

    # now we can simplify to 3x2 grid.
    grid = [[0, 0, 0], [0, 0, 0]]
    for y in range(2):
        yStart = 8 * y
        yEnd = yStart + 7
        for x in range(3):
            xStart = 4 + 8 * x
            xEnd = xStart + 7
            grid[y][x] = np.sum(img[yStart:yEnd, xStart:xEnd]) > int(49 * COUNT_PERC)

    if grid[0][0] and grid[0][1] and grid[0][2]:  # j, t, l
        if grid[1][0]:  # 1 1 1
            return "L"  # 1 ? ?

        if grid[1][1]:  # 1 1 1
            return "T"  # ? 1 ?

        if grid[1][2]:  # 1 1 1
            return "J"  # ? ? 1

        return None

    if not grid[0][0] and grid[0][1] and grid[0][2]:
        return "S"  # 0 1 1
        # ? ? ?

    if grid[0][0] and grid[0][1] and not grid[0][2]:
        return "Z"  # 1 1 0
        # ? ? ?

    # finally, check for O
    o_pixels_row1 = np.sum(img[:7, 8:22])  # perfect score is 98
    o_pixels_row2 = np.sum(img[8:, 8:22])  # perfect score is 98

    o_pixels = o_pixels_row1 > int(98 * COUNT_PERC) and o_pixels_row2 > int(
        98 * COUNT_PERC
    )
    if o_pixels:
        return "O"

    return None


if __name__ == "__main__":
    # run this from root directory as "python -m nestris_ocr.ocr_algo.preview2"
    img = Image.open("nestris_ocr/assets/test/s.png")
    import time
    from nestris_ocr.colors import Colors

    colors = Colors()

    iterations = 10000

    t = time.time()
    for i in range(iterations):
        parseImage(img, colors)
    print(time.time() - t, (time.time() - t) / iterations)
