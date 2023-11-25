# invoke from roo as python -m nestris_ocr.assets.sample_inputs.easiercap.test_color1

from PIL import Image, ImageFilter
from nestris_ocr.colors import Colors
from math import floor, ceil

blur = ImageFilter.GaussianBlur()
blur.radius = 1


def crop(source):
    return source.crop(
        (
            floor(source.width * 0.5),
            floor(source.height * 0.5),
            ceil(source.width * 0.9),
            ceil(source.height * 0.9),
        )
    )


def getColorExisting(colImg):
    return colImg.resize((1, 1), Image.LANCZOS).getpixel((0, 0))


def getColorCropBlurNearest(colImg):
    return crop(colImg).filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))


def getColorCropAntialias(colImg):
    return crop(colImg).resize((1, 1), Image.LANCZOS).getpixel((0, 0))


def getColorCropBox(colImg):
    return crop(colImg).resize((1, 1), Image.BOX).getpixel((0, 0))


methods = {
    "existing": getColorExisting,
    "cropBlurNearest": getColorCropBlurNearest,
    "cropAntialias": getColorCropAntialias,
    "cropBox": getColorCropBox,
}


def distance(pixel, color):
    r = int(pixel[0]) - int(color[0])
    g = int(pixel[1]) - int(color[1])
    b = int(pixel[2]) - int(color[2])

    return r * r + g * g + b * b


def getMatchAndDistance(field, colorsOld, colorsNew):
    total_distance = 0
    matches = 0
    differs = 0
    equal = 0
    better = 0
    worse = 0
    issues = []
    data = []

    for y in range(20):
        row = []
        data.append(row)

        for x in range(10):
            pixel = field.getpixel((x, y))

            old = [
                {"col": 0, "dist": distance(pixel, colorsOld.black)},
                {"col": 1, "dist": distance(pixel, colorsOld.white)},
                {"col": 2, "dist": distance(pixel, colorsOld.color1)},
                {"col": 3, "dist": distance(pixel, colorsOld.color2)},
            ]
            new = [
                {"col": 0, "dist": distance(pixel, colorsNew.black)},
                {"col": 1, "dist": distance(pixel, colorsNew.white)},
                {"col": 2, "dist": distance(pixel, colorsNew.color1)},
                {"col": 3, "dist": distance(pixel, colorsNew.color2)},
            ]

            old.sort(key=lambda x: x["dist"])
            new.sort(key=lambda x: x["dist"])

            row.append("%d%d" % (new[0]["col"], old[0]["col"]))

            if old[0]["col"] == new[0]["col"]:
                matches += 1
                dist = old[0]["dist"] - new[0]["dist"]
                total_distance += dist

                if dist > 0:  # old is larger than new. i.e. worse
                    better += 1
                elif dist == 0:  # old is larger than new. i.e. worse
                    equal += 1
                else:
                    worse += 1

            else:
                differs += 1
                issues.append(((x, y), pixel, new, old))

    return {
        "matches": matches,
        "equal_better_worse": (equal, better, worse),
        "differs": differs,
        "issues": issues,
        "avg_gain": total_distance / 200.0,
        "data": data,
    }


def printRes(res, method1, method2, debug=False):
    print("board")

    if debug:
        print("==========")
        for row in range(20):
            print(res["data"][row])
        print("stats")
        print("==========")

    print("matches", res["matches"])
    print("equal,better,worse", res["equal_better_worse"])
    print("differs", res["differs"])
    print("avg_gain", res["avg_gain"])

    if debug:
        print("issues")
        print("==========")
        for issue in res["issues"]:
            print(issue[0], issue[1])
            print(issue[2])
            print(issue[3])


def test(method1, method2, level, debug=False):
    print("Comparing %s vs %s" % (method1, method2))
    print("==========")
    print("level %d" % (level,))

    img_field = Image.open(
        "nestris_ocr/assets/sample_inputs/easiercap/lvl%d/field.png" % (level,)
    )
    img_col1 = Image.open(
        "nestris_ocr/assets/sample_inputs/easiercap/lvl%d/color1.png" % (level,)
    )
    img_col2 = Image.open(
        "nestris_ocr/assets/sample_inputs/easiercap/lvl%d/color2.png" % (level,)
    )

    if debug:
        img_field.show()
        img_col1.show()
        img_col2.show()

    # this is how the field is looked at to pick 10x20 unique pixels
    img_field = img_field.resize((10, 20), Image.NEAREST)

    if debug:
        img_field.show()

    getter1 = methods[method1]
    colorsM1 = Colors()
    colorsM1.setColor1Color2(getter1(img_col1), getter1(img_col2))
    print(method1, colorsM1.black, colorsM1.white, colorsM1.color1, colorsM1.color2)

    getter2 = methods[method2]
    colorsM2 = Colors()
    colorsM2.setColor1Color2(getter2(img_col1), getter2(img_col2))
    print(method2, colorsM2.black, colorsM2.white, colorsM2.color1, colorsM2.color2)

    res = getMatchAndDistance(img_field, colorsM1, colorsM2)

    printRes(res, method1, method2)

    return res


for level in range(10):
    test("cropAntialias", "cropBox", level)
