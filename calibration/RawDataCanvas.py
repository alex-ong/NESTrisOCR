import tkinter as tk
from PIL import ImageTk


class RawDataCanvas(tk.Canvas):
    def __init__(self, root):
        super().__init__(root, width=500, height=200)
        self._getImg = None
        self._img = None
        self._tmpImg = None

        self._rects = [[None for i in range(10)] for j in range(20)]
        self.ph = None
        blockSize = 10
        for y in range(len(self._rects)):
            for x in range(len(self._rects[y])):
                startX = x * blockSize
                endX = (x + 1) * blockSize
                startY = y * blockSize
                endY = (y + 1) * blockSize
                myrectangle = self.create_rectangle(
                    startX, startY, endX, endY, fill="yellow"
                )
                self._rects[y][x] = myrectangle

    def updateRect(self, x, y, color):
        self.itemconfig(self._rects[y][x], fill=color)

    def update(self):
        if self._getImg is not None:
            self.updateImage(self._getImg())

    def updateImage(self, image):
        image = image[0]
        for y in range(len(self._rects)):
            for x in range(len(self._rects[y])):
                self.updateRect(x, y, image.getData(x, y))

    def SetImageSource(self, callback):
        self._getImg = callback
