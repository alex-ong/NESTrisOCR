# invoke from roo as python -m nestris_ocr.assets.test.test_lvl7_board

from PIL import Image, ImageFilter
import time
from math import floor, ceil

big_size = 150

original_img = Image.open("nestris_ocr/assets/sample_inputs/easiercap/lvl7/color1.png")
original_img.resize((big_size, big_size), Image.NEAREST).show()

iterations = 1000

# =============================
### Current algoritm ###
# =============================

start = time.time()
for i in range(iterations):
    color = original_img.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))

elapsed = time.time() - start
print("resize antialias", elapsed, elapsed / iterations)
print("resize antialias", color)

original_img.resize((1, 1), Image.ANTIALIAS).resize(
    (big_size, big_size), Image.NEAREST
).show()


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

original_img.filter(blur).resize((big_size, big_size), Image.NEAREST).show()

original_img.filter(blur).resize((1, 1), Image.NEAREST).resize(
    (big_size, big_size), Image.NEAREST
).show()


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

img.resize((big_size, big_size), Image.NEAREST).show()
img.filter(blur).resize((big_size, big_size), Image.NEAREST).show()

start = time.time()
for i in range(iterations):
    color = img.filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))

elapsed = time.time() - start
print("crop first+blur", elapsed, elapsed / iterations)
print("crop first+blur", color)

img.filter(blur).resize((1, 1), Image.NEAREST).resize(
    (big_size, big_size), Image.NEAREST
).show()
