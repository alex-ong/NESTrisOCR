from numba.pycc import CC
from numba import njit
import numpy as np
from math import sqrt


cc = CC("board_ocr")
cc.verbose = True


@njit  # need to tell other AOT functions that this exists.
@cc.export("match_color", "uint8(float64,float64,float64,uint8[:,:])")
def match_color(pixr, pixg, pixb, colors):
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

    return closest


@cc.export("shine_parse", "uint8[:,:](uint8[:,:,:],uint8[:,:],uint8[:,:])")
def shine_parse(img, colors_bw, colors_noblack):
    # todo: maybe pass this in as a 3d array instead,
    # as numba hates python arrays
    colors_noblack_remap = [1, 2, 3]

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

            # check for white shine first.
            has_white_shine = False
            for i in range(xidx - 3, xidx):
                for j in range(yidx - 3, yidx):
                    pixr, pixg, pixb = img[j, i]
                    closest = match_color(pixr, pixg, pixb, colors_bw)
                    if closest == 1:  # white
                        has_white_shine = True
                        break
                if has_white_shine:
                    break

            if not has_white_shine:
                result[y, x] = 0  # black
                continue

            # match block using ao9 to non-black.
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

            closest = match_color(pixr, pixg, pixb, colors_noblack)
            closest = colors_noblack_remap[closest]
            result[y, x] = closest

    return result


@cc.export("ao9_parse", "uint8[:,:](uint8[:,:,:],uint8[:,:])")
def ao9_parse(img, colors):
    # todo: maybe pass this in as a 3d array instead,
    # as numba hates python arrays

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

            closest = 3
            closest = match_color(pixr, pixg, pixb, colors)

            result[y, x] = closest

    return result


@cc.export("color_dist", "uint32(uint8[:], uint8[:])")
def color_dist(color1, color2):
    # we have to do it seperately since np.subtract will be uint8
    r = color1[0] - color2[0]
    g = color1[1] - color2[1]
    b = color1[2] - color2[2]
    return r * r + g * g + b * b


if __name__ == "__main__":
    cc.compile()
