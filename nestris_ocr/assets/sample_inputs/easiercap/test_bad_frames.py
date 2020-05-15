# invoke from roo as python -m nestris_ocr.assets.sample_inputs.easiercap.test_color1
import sys
from PIL import Image
import numpy as np
from nestris_ocr.colors import Colors


def runFor(src):
    img = Image.open(src)
    scaled_img = img.resize((10, 20), Image.NEAREST)

    spanx = img.width / 10
    spany = img.height / 20

    np_img = np.array(img, dtype=np.uint16)

    np_scaled_img = np.array(scaled_img, dtype=np.uint8)

    colors = Colors()
    colors.setLevel(18)

    for y in range(20):
        row = []

        for x in range(10):
            pix = np_scaled_img[y, x]
            res_n = getColor(pix, colors)

            xidx = round(spanx * (x + 0.5))
            yidx = round(spany * (y + 0.5))

            # approach 1 straight average
            target = np_img[yidx - 1 : yidx + 2, xidx - 1 : xidx + 2]
            pix = np.average(target, axis=(0, 1))

            # approach 2 square -> average -> sqrt
            target = np.square(target)
            pix = np.average(target, axis=(0, 1))
            pix = np.sqrt(pix)

            res_a = getColor(pix, colors)

            row.append("%d%d" % (res_n, res_a))

        print(row)


def getColor(pix, colors):
    cols = [colors.black, colors.white, colors.color1, colors.color2]

    closest = 0
    lowest_dist = (256 * 256) * 3
    i = 0

    for color in cols:
        r = int(color[0]) - int(pix[0])
        g = int(color[1]) - int(pix[1])
        b = int(color[2]) - int(pix[2])

        dist = r * r + g * g + b * b

        if dist < lowest_dist:
            lowest_dist = dist
            closest = i

        i += 1

    return closest


runFor(sys.argv[1])
