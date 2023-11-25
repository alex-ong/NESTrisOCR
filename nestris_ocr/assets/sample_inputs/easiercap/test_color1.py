# invoke from roo as python -m nestris_ocr.assets.sample_inputs.easiercap.test_color1

from PIL import Image, ImageFilter
import time
from math import floor, ceil

big_size = 60
offset = 10
span = big_size + offset
num_algos = 3

blur = ImageFilter.GaussianBlur()
blur.radius = 1


result_image = Image.new("RGB", (span * 4, span * num_algos * 2 * 10), (0, 0, 0, 255))


def runFor(level, color, iterations=1):
    result_y = (span * num_algos) * (2 * level + (color - 1))

    row_idx = 0

    original_img = Image.open(
        "nestris_ocr/assets/sample_inputs/easiercap/lvl%d/color%d.png" % (level, color)
    )

    cropped = original_img.crop(
        (
            floor(original_img.width * 0.5),
            floor(original_img.height * 0.5),
            ceil(original_img.width * 0.9),
            ceil(original_img.height * 0.9),
        )
    )

    # =============================
    ### Current algoritm ###
    # =============================

    tmp = original_img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (0, result_y + row_idx * span))

    start = time.time()
    for i in range(iterations):
        color = original_img.resize((1, 1), Image.LANCZOS).getpixel((0, 0))

    elapsed = time.time() - start
    print("antialias", elapsed, elapsed / iterations)
    print("antialias", color)

    tmp = original_img.resize((1, 1), Image.LANCZOS).resize(
        (big_size, big_size), Image.NEAREST
    )
    result_image.paste(tmp, (span * 3, result_y))

    """
    # =============================
    ### Blur + resize nearest ###
    # =============================

    row_idx += 1

    tmp = original_img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (0, result_y + row_idx * span))

    start = time.time()
    for i in range(iterations):
        color = original_img.filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))

    elapsed = time.time() - start
    print("blur,nearest", elapsed, elapsed / iterations)
    print("blur,nearest", color)

    tmp = original_img.filter(blur).resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 2, result_y + row_idx * span))

    tmp = (
        original_img.filter(blur)
        .resize((1, 1), Image.NEAREST)
        .resize((big_size, big_size), Image.NEAREST)
    )
    result_image.paste(tmp, (span * 3, result_y + row_idx * span))

    # =============================
    ### Crop + blur + resize nearest ###
    # =============================

    row_idx += 1

    tmp = original_img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (0, result_y + row_idx * span))

    tmp = cropped.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 1, result_y + row_idx * span))

    tmp = cropped.filter(blur).resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 2, result_y + row_idx * span))

    start = time.time()
    for i in range(iterations):
        color = cropped.filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))

    elapsed = time.time() - start
    print("cropped,blur,nearest", elapsed, elapsed / iterations)
    print("cropped,blur,nearest", color)

    tmp = (
        cropped.filter(blur)
        .resize((1, 1), Image.NEAREST)
        .resize((big_size, big_size), Image.NEAREST)
    )
    result_image.paste(tmp, (span * 3, result_y + row_idx * span))
    """

    # =============================
    ### Crop + resize antialias ###
    # =============================

    row_idx += 1

    tmp = original_img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (0, result_y + row_idx * span))

    tmp = cropped.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 1, result_y + row_idx * span))

    start = time.time()
    for i in range(iterations):
        color = cropped.resize((1, 1), Image.LANCZOS).getpixel((0, 0))

    elapsed = time.time() - start
    print("cropped,antilias", elapsed, elapsed / iterations)
    print("cropped,antilias", color)

    tmp = cropped.resize((1, 1), Image.LANCZOS).resize(
        (big_size, big_size), Image.NEAREST
    )
    result_image.paste(tmp, (span * 3, result_y + row_idx * span))

    # =============================
    ### Crop + resize box ###
    # =============================

    row_idx += 1

    tmp = original_img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (0, result_y + row_idx * span))

    tmp = cropped.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 1, result_y + row_idx * span))

    start = time.time()
    for i in range(iterations):
        color = cropped.resize((1, 1), Image.BOX).getpixel((0, 0))

    elapsed = time.time() - start
    print("cropped,box", elapsed, elapsed / iterations)
    print("cropped,box", color)

    tmp = cropped.resize((1, 1), Image.BOX).resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 3, result_y + row_idx * span))


"""
for level in range(10):
    for color in [1, 2]:
        runFor(level, color)

result_image.show()
"""

runFor(1, 1, 1000000)
