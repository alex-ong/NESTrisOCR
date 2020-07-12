import tkinter as tk
import numpy as np
from PIL import Image

from nestris_ocr.colors import Colors
from nestris_ocr.calibration.image_canvas import ImageCanvas
from nestris_ocr.utils.lib import tryGetInt
from nestris_ocr.ocr_state.field_state import FieldState


class FieldView(ImageCanvas):
    def __init__(self, root, width, height):
        super().__init__(root, width, height)
        self.color_table = Colors()
        self.current_level = None
        self.color_table.setLevel(0)

    def updateField(self, field, level):
        success, level = tryGetInt(level)
        if success and level != self.current_level:
            self.color_table.setLevel(level)

        field = convert_field(field)

        lut = np.array(self.color_table.colors)
        image = lut[field]
        # TODO: check out lut.take which might be faster
        image = Image.fromarray(image, "RGB")
        image = image.resize((self.width, self.height), Image.NEAREST)
        self.updateImage(image)


# convert from string or fieldstate to numpy array.
def convert_field(field):
    if isinstance(field, str):  # convert back to numpy array...
        field = convertStringField(field)

    if isinstance(field, FieldState):
        field = field.data

    if not isinstance(field, np.ndarray):
        raise TypeError("Cannot convert field to correct type: " + str(type(field)))

    return field


# convert string field to numpy array.
def convertStringField(strfield):
    field = np.zeros((200,), dtype=np.uint8)
    for index, item in enumerate(strfield):
        field[index] = int(item)
    field = np.reshape(field, (20, 10))
    return field


def sample_data():
    import random

    field = np.zeros((20, 10), dtype=np.uint8)
    for y in range(20):
        for x in range(10):
            field[y, x] = random.randint(0, 3)
    return field


# simple test
if __name__ == "__main__":
    root = tk.Tk()
    fv = FieldView(root, 100, 200)
    fv.pack()

    field = sample_data()
    fv.updateField(field, 18)
    root.mainloop()
