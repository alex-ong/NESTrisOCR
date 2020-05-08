# invoke from roo as python -m nestris_ocr.assets.sample_inputs.easiercap.test_color1

from PIL import Image, ImageFilter
import time
from math import floor, ceil

big_size = 60
offset = 10
span = big_size + offset

result_image = Image.new("RGB", (span * 4, span * 3 * 2 * 10), (0, 0, 0, 255))


def runFor(level, color, iterations=1):
    result_y = (span * 3) * (2 * level + (color - 1))

    original_img = Image.open(
        "nestris_ocr/assets/sample_inputs/easiercap/lvl%d/color%d.png" % (level, color)
    )

    tmp = original_img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (0, result_y))
    result_image.paste(tmp, (0, result_y + span))
    result_image.paste(tmp, (0, result_y + span * 2))

    # =============================
    ### Current algoritm ###
    # =============================

    start = time.time()
    for i in range(iterations):
        color = original_img.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))

    elapsed = time.time() - start
    print("resize antialias", elapsed, elapsed / iterations)
    print("resize antialias", color)

    tmp = original_img.resize((1, 1), Image.ANTIALIAS).resize(
        (big_size, big_size), Image.NEAREST
    )
    result_image.paste(tmp, (span * 3, result_y))

    # =============================
    ### Blur + resize nearest ###
    # =============================

    blur = ImageFilter.GaussianBlur()
    blur.radius = 1

    start = time.time()
    for i in range(iterations):
        color = original_img.filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))

    elapsed = time.time() - start
    print("blur", elapsed, elapsed / iterations)
    print("blur", color)

    tmp = original_img.filter(blur).resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 2, result_y + span))

    tmp = (
        original_img.filter(blur)
        .resize((1, 1), Image.NEAREST)
        .resize((big_size, big_size), Image.NEAREST)
    )
    result_image.paste(tmp, (span * 3, result_y + span))

    # =============================
    ### Crop First + blur + resize nearest ###
    # =============================

    img = original_img.crop(
        (
            floor(original_img.width * 0.5),
            floor(original_img.height * 0.5),
            ceil(original_img.width * 0.9),
            ceil(original_img.height * 0.9),
        )
    )

    tmp = img.resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 1, result_y + span * 2))

    tmp = img.filter(blur).resize((big_size, big_size), Image.NEAREST)
    result_image.paste(tmp, (span * 2, result_y + span * 2))

    start = time.time()
    for i in range(iterations):
        color = img.filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))

    elapsed = time.time() - start
    print("crop first+blur", elapsed, elapsed / iterations)
    print("crop first+blur", color)

    tmp = (
        img.filter(blur)
        .resize((1, 1), Image.NEAREST)
        .resize((big_size, big_size), Image.NEAREST)
    )
    result_image.paste(tmp, (span * 3, result_y + span * 2))


for level in range(10):
    for color in [1, 2]:
        runFor(level, color)

result_image.show()
