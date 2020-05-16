import numpy as np
from numba import njit
from math import sqrt

# atm this takes 12 millseconds to complete, with jit it takes <1ms.
# we want to eventually compile this numba AOT, so we don't need numba.


@njit("uint8[:,:](uint8[:,:,:],uint8[:],uint8[:],uint8[:],uint8[:])")
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

            # max value is 256*256*9
            pix = np.zeros(3, dtype=np.uint32)

            # grab 9 pixels in a 3x3 square
            # and compute average
            for i in range(xidx - 1, xidx + 2):
                for j in range(yidx - 1, yidx + 2):
                    tmp = img[j, i]
                    pix[0] += tmp[0] * tmp[0]
                    pix[1] += tmp[1] * tmp[1]
                    pix[2] += tmp[2] * tmp[2]

            pix[0] = round(sqrt(pix[0] / 9))
            pix[1] = round(sqrt(pix[1] / 9))
            pix[2] = round(sqrt(pix[2] / 9))

            closest = 0
            lowest_dist = (256 * 256) * 3

            for i, color in enumerate(colors):
                r = color[0] - pix[0]
                g = color[1] - pix[1]
                b = color[2] - pix[2]

                dist = r * r + g * g + b * b

                if dist < lowest_dist:
                    lowest_dist = dist
                    closest = i

            result[y, x] = closest

    return result
