import numpy as np
from numba import njit
from math import sqrt

# atm this takes 12 millseconds to complete, with jit it takes <1ms.
# we want to eventually compile this numba AOT, so we don't need numba.


@njit(
    "uint8[:,:](uint8[:,:,:],uint8[:],uint8[:],uint8[:],uint8[:])",
    nogil=True,
    cache=True,
)
def parseImage2(img, black, white, color1, color2):

    # todo: maybe pass this in as a 3d array instead,
    # as numba hates python arrays
    # colors = [black, white, color1, color2]
    colors_noblack = [white, color1, color2]
    colors_noblack_remap = [1, 2, 3]
    colors_bw = [black, white]

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

            has_white_shine = False

            for i in range(xidx - 3, xidx):
                for j in range(yidx - 3, yidx):
                    lowest_dist = (256 * 256) * 3
                    closest = -1
                    pixr, pixg, pixb = img[j, i]

                    for c, color in enumerate(colors_bw):
                        r = color[0] - pixr
                        g = color[1] - pixg
                        b = color[2] - pixb

                        dist = r * r + g * g + b * b
                        if dist < lowest_dist:
                            lowest_dist = dist
                            closest = c

                    if closest == 1:  # white
                        has_white_shine = True
                        break

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

            if has_white_shine:
                available_colors = colors_noblack
                for i, color in enumerate(available_colors):
                    r = color[0] - pixr
                    g = color[1] - pixg
                    b = color[2] - pixb

                    dist = r * r + g * g + b * b

                    if dist < lowest_dist:
                        lowest_dist = dist
                        closest = i

                closest = colors_noblack_remap[closest]
            else:
                closest = 0  # black

            result[y, x] = closest

    return result
