from typing import Tuple
import numpy as np


LTRBBox = Tuple[int, int, int, int]
XYWHBox = Tuple[int, int, int, int]

Color = Tuple[int, int, int]


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

    def setBlackWhite(self, black=(0, 0, 0), white=(255, 255, 255)):
        self.black = np.array(black, dtype=np.uint8)
        self.black_luma = Colors.luma(black)
        self.white = np.array(white, dtype=np.uint8)
        self.white_luma = Colors.luma(white)
