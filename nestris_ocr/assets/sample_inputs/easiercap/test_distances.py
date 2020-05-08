# invoke from roo as python -m nestris_ocr.assets.sample_inputs.easiercap.test_color1

from PIL import Image, ImageFilter
from nestris_ocr.colors import Colors
from math import floor, ceil

blur = ImageFilter.GaussianBlur()
blur.radius = 1


def getColorOld(colImg):
    return colImg.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))


def getColorNew(colImg):
    tmp = colImg.crop(
        (
            floor(colImg.width * 0.5),
            floor(colImg.height * 0.5),
            ceil(colImg.width * 0.9),
            ceil(colImg.height * 0.9),
        )
    )

    return tmp.filter(blur).resize((1, 1), Image.NEAREST).getpixel((0, 0))


def distance(pixel, color):
    r = int(pixel[0]) - int(color[0])
    g = int(pixel[1]) - int(color[1])
    b = int(pixel[2]) - int(color[2])

    return r * r + g * g + b * b


def getMatchAndDistance(field, colorsOld, colorsNew):
    total_distance = 0
    matches = 0
    differs = 0
    better = 0
    equal = 0
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
                if dist == 0:  # old is larger than new. i.e. worse
                    equal += 1

            else:
                differs += 1
                issues.append(((x, y), pixel, new, old))

    return {
        "matches": matches,
        "better_and_equal": (better, equal),
        "differs": differs,
        "issues": issues,
        "avg_gain": total_distance / 200.0,
        "data": data,
    }


def printRes(res, debug=False):
    print("board")

    if debug:
        print("==========")
        for row in range(20):
            print(res["data"][row])
        print("stats")
        print("==========")

    print("matches", res["matches"])
    print("better_and_equal", res["better_and_equal"])
    print("differs", res["differs"])
    print("avg_gain", res["avg_gain"])

    if debug:
        print("issues")
        print("==========")
        for issue in res["issues"]:
            print(issue[0], issue[1])
            print(issue[2])
            print(issue[3])


def test(level, debug=False):
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

    img_field = img_field.resize((10, 20), Image.NEAREST)

    if debug:
        img_field.show()

    colorsOld = Colors()
    colorsOld.setColor1Color2(getColorOld(img_col1), getColorOld(img_col2))
    print("old", colorsOld.black, colorsOld.white, colorsOld.color1, colorsOld.color2)

    colorsNew = Colors()
    colorsNew.setColor1Color2(getColorNew(img_col1), getColorNew(img_col2))
    print("new", colorsNew.black, colorsNew.white, colorsNew.color1, colorsNew.color2)

    res = getMatchAndDistance(img_field, colorsOld, colorsNew)

    printRes(res)

    return res


for level in range(10):
    test(level)
