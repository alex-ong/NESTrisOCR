from nestris_ocr.colors import Colors
from nestris_ocr.calibration.image_canvas import ImageCanvas
import tkinter as tk
import numpy as np
from PIL import Image


class FieldView(ImageCanvas):
    def __init__(self, root, width, height):
        super().__init__(root, width, height)
        self.color_table = Colors()
        self.current_level = None
        self.color_table.setLevel(0)

    
    def updateField(self, field, level):
        if level is not None and level != self.current_level:
            self.color_table.setLevel(level)
        
        lut = np.array(self.color_table.colors)
        image = lut[field]
        # TODO: check out lut.take which might be faster
        image = Image.fromarray(image, "RGB")
        image = image.resize((self.width, self.height))
        self.updateImage(image)

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
