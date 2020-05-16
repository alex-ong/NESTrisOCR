from numba.pycc import CC
import numpy as np
from math import sqrt

cc = CC("board_ocr")
cc.verbose = True


@cc.export(
    "parseImage2", "uint8[:,:](uint8[:,:,:],uint8[:],uint8[:],uint8[:],uint8[:])"
)
def parseImage2(img, black, white, color1, color2):

    # todo: maybe pass this in as a 3d array instead,
    # as numba hates python arrays
    colors = [black, white, color1, color2]

    spanx = img.shape[1] / 10
    spany = img.shape[0] / 20

    result = np.zeros((20, 10), dtype=np.uint8)

    for x in range(10):
        for y in range(20):
            xidx = round(spanx * (x + 0.5))
            yidx = round(spany * (y + 0.5))

            pixr = 0
            pixg = 0
            pixb = 0

            # grab 9 pixels in a 3x3 square
            # and compute average
            for i in range(xidx - 1, xidx + 2):
                for j in range(yidx - 1, yidx + 2):
                    tmp = img[j, i]
                    pixr += tmp[0] * tmp[0]
                    pixg += tmp[1] * tmp[1]
                    pixb += tmp[2] * tmp[2]

            pixr = sqrt(pixr / 9)
            pixg = sqrt(pixg / 9)
            pixb = sqrt(pixb / 9)

            closest = 0
            lowest_dist = (256 * 256) * 3

            for i, color in enumerate(colors):
                r = color[0] - pixr
                g = color[1] - pixg
                b = color[2] - pixb

                dist = r * r + g * g + b * b

                if dist < lowest_dist:
                    lowest_dist = dist
                    closest = i

            result[y, x] = closest

    return result


if __name__ == "__main__":
    cc.compile()
