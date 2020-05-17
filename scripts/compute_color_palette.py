# invoke from root as python3 -m scripts.compute_color_palette easiercap nestris_ocr/assets/sample_inputs/easiercap/lvl%d/field.png
import json
import sys
from PIL import Image, ImageFilter
import numpy as np
from nestris_ocr.colors import Colors
from math import sqrt


def getColors(level, field):
    img = Image.open(field)

    # extra smoothness from PIL
    slight_blur = ImageFilter.GaussianBlur()
    slight_blur.radius = 1

    img = img.filter(slight_blur)

    spanx = img.width / 10
    spany = img.height / 20

    np_img = np.array(img, dtype=np.uint16)

    colors = Colors()
    colors.setLevel(level)

    color_instances = ([], [], [], [])

    for y in range(20):
        for x in range(10):
            xidx = round(spanx * (x + 0.5))
            yidx = round(spany * (y + 0.5))

            pix = [0, 0, 0]

            # grab 9 pixels in a 3x3 square for each block
            # on the lower-right quadrant
            # and compute color average
            for i in range(xidx, xidx + 3):
                for j in range(yidx, yidx + 3):
                    tmp = np_img[j, i]
                    pix[0] += tmp[0] * tmp[0]
                    pix[1] += tmp[1] * tmp[1]
                    pix[2] += tmp[2] * tmp[2]

            pix[0] = sqrt(pix[0] / 9)
            pix[1] = sqrt(pix[1] / 9)
            pix[2] = sqrt(pix[2] / 9)

            col_index = colors.getClosestColorIndex(pix)

            color_instances[col_index].append(pix)

    # average the colors
    col1 = (
        round(sum([c[0] for c in color_instances[2]]) / len(color_instances[2])),
        round(sum([c[1] for c in color_instances[2]]) / len(color_instances[2])),
        round(sum([c[2] for c in color_instances[2]]) / len(color_instances[2])),
    )

    col2 = (
        round(sum([c[0] for c in color_instances[3]]) / len(color_instances[3])),
        round(sum([c[1] for c in color_instances[3]]) / len(color_instances[3])),
        round(sum([c[2] for c in color_instances[3]]) / len(color_instances[3])),
    )

    return col1, col2


def getPalette(field_path_template):
    colors = []

    for level in range(10):
        cols = getColors(level, field_path_template % (level,))
        colors.append(cols)

    return colors


def getPaletteImage(palette):
    # prepare visual aid to show the difference between reference colors and read colors
    palette_block_size = 50
    palette_gap_size = 2

    palette_img = Image.new(
        "RGB",
        (
            (palette_block_size + palette_gap_size) * 2 - palette_gap_size,
            (palette_block_size + palette_gap_size) * 10 - palette_gap_size,
        ),
        (0, 0, 0, 255),
    )

    for level in range(10):
        col1, col2 = palette[level]

        col1 = Image.new("RGB", (1, 1), tuple(col1))
        col2 = Image.new("RGB", (1, 1), tuple(col2))

        palette_img.paste(
            col1.resize((palette_block_size, palette_block_size), Image.NEAREST),
            (0, (palette_block_size + palette_gap_size) * level),
        )

        palette_img.paste(
            col2.resize((palette_block_size, palette_block_size), Image.NEAREST),
            (
                (palette_block_size + palette_gap_size),
                (palette_block_size + palette_gap_size) * level,
            ),
        )

    return palette_img


if __name__ == "__main__":
    palette_name = sys.argv[1]
    field_path_template = sys.argv[2]

    colors = Colors()

    palette = getPalette(field_path_template)
    palette_img = getPaletteImage(palette)

    with open("nestris_ocr/palettes/%s.json" % (palette_name,), "w") as outfile:
        json.dump(palette, outfile)

    palette_img.save("nestris_ocr/palettes/%s.png" % (palette_name,))

    # show both reference palette and computed palette for comparison
    palette_img.show()
    getPaletteImage(colors.palette).show()
