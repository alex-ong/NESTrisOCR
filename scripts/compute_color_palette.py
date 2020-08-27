# invoke from root as python3 -m scripts.compute_color_palette easiercap nestris_ocr/assets/sample_inputs/easiercap/lvl%d/field.png
import json
import sys
from PIL import Image
import numpy as np
from nestris_ocr.colors import Colors
from math import sqrt


def getAverageColor(pixels):
    return (
        round(sqrt(sum([p[0] * p[0] for p in pixels]) / len(pixels))),
        round(sqrt(sum([p[1] * p[1] for p in pixels]) / len(pixels))),
        round(sqrt(sum([p[2] * p[2] for p in pixels]) / len(pixels))),
    )


def getColors(level, field):
    img = Image.open(field)

    res_img = Image.new(
        "RGBA",
        (img.width, img.height),
        (0, 0, 0, 255),
    )

    res_img.paste(img.convert("RGBA"), (img.width * 0, 0))

    # nes pix size, block span and capture are only valid on perfect calibration
    # perfect calibration implies capturing the right and bottom black edges
    # still, since we're capturing a safe zone, things should still work with small discrepancies

    nes_pixels_to_sample = (
        (2, 4.5),
        (4.5, 2),
        (4.5, 4.5),
    )

    nes_pix_xsize = img.width / 80
    nes_pix_ysize = img.height / 160

    spanx = nes_pix_xsize * 8
    spany = nes_pix_ysize * 8

    corner_highlight = Image.new("RGBA", (1, 1), (255, 0, 0, 128))
    capture_highlight = Image.new("RGBA", (1, 1), (0, 255, 0, 128))

    np_img = np.array(img, dtype=np.uint16)

    colors = Colors()
    colors.setLevel(level)

    color_instances = ([], [], [], [])

    for y in range(20):
        for x in range(10):
            xidx = spanx * x
            yidx = spany * y

            # print the top-left corner
            res_img.paste(
                corner_highlight, (round(xidx), round(yidx)), corner_highlight
            )

            pixels = []

            for offsetx, offsety in nes_pixels_to_sample:
                right = round(xidx + nes_pix_xsize * offsetx)
                top = round(yidx + nes_pix_ysize * offsety)
                left = round(xidx + nes_pix_xsize * (offsetx + 1))
                bottom = round(yidx + nes_pix_ysize * (offsety + 1))

                cap = capture_highlight.resize((left - right, bottom - top))

                res_img.paste(cap, (right, top), cap)

                # grab all pixels in the capture area
                for i in range(right, left):
                    for j in range(top, bottom):
                        pixels.append(np_img[j, i])

            pix = getAverageColor(pixels)

            col_index = colors.getClosestColorIndex(pix)

            color_instances[col_index].extend(pixels)

    if level == 0:
        res_img.convert("RGB").resize((img.width * 3, img.height * 3)).show()

    # average the colors
    col1 = getAverageColor(color_instances[2])
    col2 = getAverageColor(color_instances[3])

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

    palette_img.show()

    # shows the default palette for comparison
    # getPaletteImage(colors.palette).show()
