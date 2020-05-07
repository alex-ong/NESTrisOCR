from typing import Tuple
import numpy as np
from nestris_ocr.utils.lib import ilerp

Color = Tuple[int, int, int]

LUMA_OFFSET = 15

REFERENCE_LEVEL_COLORS = (
    ((0x4A, 0x32, 0xFF), (0x4A, 0xAF, 0xFE)),
    ((0x00, 0x96, 0x00), (0x6A, 0xDC, 0x00)),
    ((0xB0, 0x00, 0xD4), (0xFF, 0x56, 0xFF)),
    ((0x4A, 0x32, 0xFF), (0x00, 0xE9, 0x00)),
    ((0xC8, 0x00, 0x7F), (0x00, 0xE6, 0x78)),
    ((0x00, 0xE6, 0x78), (0x96, 0x8D, 0xFF)),
    ((0xC4, 0x1E, 0x0E), (0x66, 0x66, 0x66)),
    ((0x82, 0x00, 0xFF), (0x78, 0x00, 0x41)),
    ((0x4A, 0x32, 0xFF), (0xC4, 0x1E, 0x0E)),
    ((0xC4, 0x1E, 0x0E), (0xF6, 0x9B, 0x00)),
)

REFERENCE_LEVEL_COLORS = [
    (np.array(color1, dtype=np.uint8), np.array(color2, dtype=np.uint8))
    for color1, color2 in REFERENCE_LEVEL_COLORS
]


class Colors:
    black: Color
    white: Color
    color1: Color
    color2: Color
    black_luma: float
    white_luma: float

    @staticmethod
    def luma(pixel):
        # ITU-R 601-2 luma transform
        # See https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.convert
        return pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114

    def __init__(
        self, black=(0, 0, 0), white=(255, 255, 255), color1=None, color2=None
    ):
        self.setBlackWhite(black, white)
        self.setColor1Color2(color1, color2)
        pass

    def setColor1Color2(self, color1, color2):
        self.color1 = np.array(color1 or (0, 0, 0), dtype=np.uint8)
        self.color2 = np.array(color2 or (0, 0, 0), dtype=np.uint8)

    def setBlackWhite(self, black, white):
        self.black = np.array(black, dtype=np.uint8)
        self.black_luma = Colors.luma(black) + LUMA_OFFSET
        self.white = np.array(white, dtype=np.uint8)
        self.white_luma = Colors.luma(white) - LUMA_OFFSET

    def setLevel(self, level, interpolate=False):  # caller must pass a valid int level
        color1, color2 = REFERENCE_LEVEL_COLORS[level % 10]

        if interpolate:
            black = self.black
            white = self.white

            # TODO: should interpolation be done with channel squaring?
            # See: https://www.youtube.com/watch?v=LKnqECcg6Gw

            color1 = (
                ilerp(black[0], white[0], color1[0] / 0xFF),
                ilerp(black[1], white[1], color1[1] / 0xFF),
                ilerp(black[2], white[2], color1[2] / 0xFF),
            )
            color1 = np.array(color1, dtype=np.uint8)

            color2 = (
                ilerp(black[0], white[0], color2[0] / 0xFF),
                ilerp(black[1], white[1], color2[1] / 0xFF),
                ilerp(black[2], white[2], color2[2] / 0xFF),
            )
            color2 = np.array(color2, dtype=np.uint8)

        self.color1 = color1
        self.color2 = color2

    def isBlack(self, pixel):
        return Colors.luma(pixel) <= self.black_luma
