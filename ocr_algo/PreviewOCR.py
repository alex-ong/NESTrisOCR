from config import config
from lib import lerp
from PIL import Image, ImageEnhance

cachedOffsets = []
cachedPPP = None

PreviewImageSize = (31, 15)

# assuming that we have a 31 NES pixel by 15 NES Pixel capture area:
pixOffsets = ((10, 12), (17, 12), (21, 12))


# only used by calibrator
def calculateOffsets():
    baseRect = config["calibration.pct.preview"]
    global cachedPPP
    global cachedOffsets
    if baseRect != cachedPPP:
        left, right, top, bottom = (
            baseRect[0],
            baseRect[0] + baseRect[2],
            baseRect[1],
            baseRect[1] + baseRect[3],
        )
        p1 = (
            lerp(left, right, (pixOffsets[0][0]) / 31.0),
            lerp(top, bottom, (pixOffsets[0][1]) / 15.0),
        )
        p2 = (
            lerp(left, right, (pixOffsets[1][0]) / 31.0),
            lerp(top, bottom, (pixOffsets[1][1]) / 15.0),
        )
        p3 = (
            lerp(left, right, (pixOffsets[2][0]) / 31.0),
            lerp(top, bottom, (pixOffsets[2][1]) / 15.0),
        )
        cachedOffsets = [p1, p2, p3]
        cachedPPP = baseRect

    return cachedOffsets


def isNotBlack(pixel):
    return pixel[0] > 25 or pixel[1] > 25 or pixel[2] > 25


# look at assets/doc for description
def parseImage(img):
    img = img.resize(PreviewImageSize, Image.BOX)
    img = ImageEnhance.Contrast(img).enhance(3.0)
    o = isNotBlack(img.getpixel(pixOffsets[0]))
    r = isNotBlack(img.getpixel(pixOffsets[1]))
    p = isNotBlack(img.getpixel(pixOffsets[2]))

    return whichPiece(o, r, p)


# we could construct a bit lookup table instead with o << 2 + r << 1 + p
def whichPiece(o, r, p):
    if o:
        if r:
            if p:
                return "O"
            return "S"
        return "L"
    elif r:
        if p:
            return "Z"
        return "T"
    elif p:
        return "J"
    else:
        return "I"


if __name__ == "__main__":
    # run this from parent directory as "python -m ocr_algo.PreviewOCR2"
    img = Image.open("assets/test/s.png")
    import time

    t = time.time()
    for i in range(10000):
        parseImage(img)
    print(time.time() - t, (time.time() - t) / 10000)
