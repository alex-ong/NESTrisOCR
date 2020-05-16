import json
from typing import Tuple
import numpy as np
from nestris_ocr.utils.lib import ilerp

Color = Tuple[int, int, int]

LUMA_OFFSET = 15

# load the default palette from file
with open("nestris_ocr/palettes/DEFAULT.json", "r") as file:
    REFERENCE_LEVEL_COLORS = json.load(file)


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
        self.black = None
        self.white = None
        self.color1 = None
        self.color2 = None

        self.setPalette(REFERENCE_LEVEL_COLORS)
        self.setBlackWhite(black, white)
        self.setColor1Color2(color1, color2)

    def _buildColorList(self):
        self.colors = (
            self.black,
            self.white,
            self.color1,
            self.color2,
        )

    def setPalette(self, palette):
        self.palette = [
            (np.array(color1, dtype=np.uint8), np.array(color2, dtype=np.uint8))
            for color1, color2 in palette
        ]

    def setColor1Color2(self, color1, color2):
        self.color1 = np.array(color1 or (0, 0, 0), dtype=np.uint8)
        self.color2 = np.array(color2 or (0, 0, 0), dtype=np.uint8)

        self._buildColorList()

    def setBlackWhite(self, black, white):
        self.black = np.array(black, dtype=np.uint8)
        self.black_luma = Colors.luma(black) + LUMA_OFFSET
        self.white = np.array(white, dtype=np.uint8)
        self.white_luma = Colors.luma(white) - LUMA_OFFSET

        self._buildColorList()

    def setLevel(self, level, interpolate=False):  # caller must pass a valid int level
        color1, color2 = self.palette[level % 10]

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

        self._buildColorList()

    def isBlack(self, pixel):
        return Colors.luma(pixel) <= self.black_luma

    def getColorByIndex(self, index):
        return self.colors[index]

    # can a class method alone be njited?
    def getClosestColorIndex(self, pixel):
        closest = 0
        lowest_dist = (256 * 256) * 3
        i = 0

        for color in self.colors:
            r = int(color[0]) - int(pixel[0])
            g = int(color[1]) - int(pixel[1])
            b = int(color[2]) - int(pixel[2])

            dist = r * r + g * g + b * b

            if dist < lowest_dist:
                lowest_dist = dist
                closest = i

            i += 1

        return closest
