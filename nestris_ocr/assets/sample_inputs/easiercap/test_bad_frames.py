# invoke from roo as python -m nestris_ocr.assets.sample_inputs.easiercap.test_color1
import sys
from PIL import Image
import numpy as np
from nestris_ocr.colors import Colors
from math import floor, sqrt


def runFor(src, level):
    img = Image.open(src)

    scaled_img_old = img.resize((10, 20), Image.NEAREST)

    o_width = img.width + img.height
    o_height = img.height * 2

    result_img = Image.new("RGB", (o_width, o_height), (0, 0, 0, 255))
    result_img.paste(img, (0, 0))
    result_img.paste(img, (0, img.height))

    result_img.paste(
        scaled_img_old.resize((floor(img.height / 2), img.height), Image.NEAREST),
        (img.width, 0),
    )

    scaled_img_new = Image.new("RGB", (10, 20), (0, 0, 0, 255))
    res_img_old = Image.new("RGB", (10, 20), (0, 0, 0, 255))
    res_img_new = Image.new("RGB", (10, 20), (0, 0, 0, 255))

    spanx = img.width / 10
    spany = img.height / 20

    np_img = np.array(img, dtype=np.uint16)

    np_scaled_img = np.array(scaled_img_old, dtype=np.uint8)

    colors = Colors()
    colors.setLevel(level)

    cols = [colors.black, colors.white, colors.color1, colors.color2]

    for y in range(20):
        for x in range(10):
            pix = np_scaled_img[y, x]
            col_old = getColor(pix, cols)
            res_img_old.putpixel((x, y), tuple(cols[col_old]))

            xidx = round(spanx * (x + 0.5))
            yidx = round(spany * (y + 0.5))

            target = np_img[yidx - 1 : yidx + 2, xidx - 1 : xidx + 2]

            pix = [0, 0, 0]

            # grab 9 pixels in a 3x3 square
            # and compute average
            for i in range(3):
                for j in range(3):
                    tmp = target[i, j]
                    pix[0] += tmp[0] * tmp[0]
                    pix[1] += tmp[1] * tmp[1]
                    pix[2] += tmp[2] * tmp[2]

            pix[0] = int(sqrt(pix[0] / 9))
            pix[1] = int(sqrt(pix[1] / 9))
            pix[2] = int(sqrt(pix[2] / 9))

            col_new = getColor(pix, cols)

            scaled_img_new.putpixel((x, y), tuple(pix))
            res_img_new.putpixel((x, y), tuple(cols[col_new]))

    result_img.paste(
        scaled_img_new.resize((floor(img.height / 2), img.height), Image.NEAREST),
        (img.width, img.height),
    )

    result_img.paste(
        res_img_old.resize((floor(img.height / 2), img.height), Image.NEAREST),
        (img.width + floor(img.height / 2), 0),
    )

    result_img.paste(
        res_img_new.resize((floor(img.height / 2), img.height), Image.NEAREST),
        (img.width + floor(img.height / 2), img.height),
    )

    result_img.show()


def getColor(pix, cols):
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


runFor(sys.argv[1], 18)
