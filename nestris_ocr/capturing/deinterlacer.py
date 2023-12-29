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


class Field(Enum):
    TOP = 0
    BOTTOM = 1
    BOTH = 2


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


def get_mode_res():
    mode = InterlaceMode.from_string(config["capture.deinterlace_method"])
    res = InterlaceRes.from_string(config["capture.deinterlace_res"])
    # hack: we should do some business logic elsewhere to disable de-interlacing
    # on devices that don't support it?
    if config["capture.method"] != "OPENCV":
        mode = InterlaceMode.NONE
    return mode, res


# Note that the arrays returned use np magic, so no memcpy
# occurs. When a PIL.Image is generated from them, only then
# is memory re-arranged. E.g. TOP_FIELD would just
# make all iterators for the returned "array" reference the
# original array but skip every other field.
def sub_image_np(img, res, field):
    if res == InterlaceRes.FULL:
        if field == Field.TOP:
            return img[::2, :, :]
        elif field == Field.BOTTOM:
            return img[1::2, :, :]
        elif field == Field.BOTH:
            return img[:, :, :]
    elif res == InterlaceRes.HALF:
        if field == Field.TOP:
            return img[::2, ::2, :]
        elif field == Field.BOTTOM:
            return img[1::2, ::2, :]
        elif field == Field.BOTH:
            return img[::2, ::2, :]


# de-interlaces an open-cv formatted image as fast as possible
def deinterlace_np(img):
    mode, res = get_mode_res()

    if mode == InterlaceMode.NONE:
        img = sub_image_np(img, res, Field.BOTH)
        return img, None

    # x, y, rgb
    top = None
    bottom = None
    if mode != InterlaceMode.DISCARD_TOP:
        top = sub_image_np(img, res, Field.TOP)
    if mode != InterlaceMode.DISCARD_BOTTOM:
        bottom = sub_image_np(img, res, Field.BOTTOM)

    if mode == InterlaceMode.DISCARD_TOP:
        return bottom, None
    elif mode == InterlaceMode.DISCARD_BOTTOM:
        return top, None
    elif mode == InterlaceMode.TOP_FIRST:
        return top, bottom
    elif mode == InterlaceMode.BOTTOM_FIRST:
        return bottom, top


# de-interlaces a PIL.Image
def deinterlace(img):
    mode, res = get_mode_res()

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
