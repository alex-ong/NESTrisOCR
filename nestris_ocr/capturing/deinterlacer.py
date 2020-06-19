from PIL import Image
from enum import Enum
from nestris_ocr.config import config


# fastest 60p is HALF+TOP_FIRST or BOTTOM_FIRST.
# Note that if you de-interlace, Full will be Halfheight, full width.
class InterlaceRes(Enum):
    FULL = 0
    HALF = 1

    @classmethod
    def from_string(cls, value):
        if value == "FULL":
            return InterlaceRes.FULL
        elif value == "HALF":
            return InterlaceRes.HALF
        else:
            return InterlaceRes.FULL


class InterlaceMode(Enum):
    NONE = 1
    DISCARD_TOP = 2
    DISCARD_BOTTOM = 3
    TOP_FIRST = 4
    BOTTOM_FIRST = 5

    @classmethod
    def from_string(cls, value):
        if value == "NONE":
            return InterlaceMode.NONE
        elif value == "DISCARD_TOP":
            return InterlaceMode.DISCARD_TOP
        elif value == "DISCARD_BOTTOM":
            return InterlaceMode.DISCARD_BOTTOM
        elif value == "TOP_FIRST":
            return InterlaceMode.TOP_FIRST
        elif value == "BOTTOM_FIRST":
            return InterlaceMode.BOTTOM_FIRST
        else:
            return InterlaceMode.NONE


def deinterlace(img):

    mode = InterlaceMode.from_string(config["capture.deinterlace_method"])
    res = InterlaceRes.from_string(config["capture.deinterlace_res"])
    full_size = list(img.size)
    half_size = (img.size[0] // 2, img.size[1] // 2)

    if res == InterlaceRes.FULL:
        target_size = full_size
    else:
        target_size = half_size

    if mode == InterlaceMode.NONE:
        if res == InterlaceRes.FULL:
            return img, None
        elif res == InterlaceRes.HALF:
            img = img.resize(half_size, Image.NEAREST)
            return img, None

    # speedhack for non-full: we can remove horizontal resolution first.
    if res != InterlaceRes.FULL:
        img = img.resize((target_size[0], full_size[1]), Image.NEAREST)

    if mode != InterlaceMode.DISCARD_TOP:
        top = img.resize(
            (target_size[0], half_size[1]), Image.NEAREST
        )  # NEAREST drops the lines
    else:
        top = None

    if mode != InterlaceMode.DISCARD_BOTTOM:
        bottom = img.crop([0, 1, img.size[0], img.size[1]])
        img.paste(bottom)
        bottom = img.resize((target_size[0], half_size[1]), Image.NEAREST)
        bottom_shift = bottom.crop([0, 0, bottom.size[0], bottom.size[1] - 1])
        bottom.paste(bottom_shift, (0, 1))
        # use this code to identify bottom field.
        # drawer = ImageDraw.Draw(bottom)
        # drawer.rectangle([(0,0),(20,20)], fill= "#FF0000")
    else:
        bottom = None

    if mode == InterlaceMode.DISCARD_TOP:
        return bottom, None
    elif mode == InterlaceMode.DISCARD_BOTTOM:
        return top, None
    elif mode == InterlaceMode.TOP_FIRST:
        return top, bottom
    else:
        return bottom, top
