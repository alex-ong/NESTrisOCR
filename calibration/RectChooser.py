import tkinter as tk
from calibration.NumberChooser import NumberChooser, CompactNumberChooser

from lib import tryGetInt
from lib import tryGetFloat


class RectChooser(tk.Frame):
    def __init__(self, root, name, defaultValue, isFloat, OnChange):
        super().__init__(root)
        self.OnChange = OnChange
        a, b, c, d = defaultValue

        tk.Label(self, text=name).grid(row=0, columnspan=4, sticky="nsew")
        minCrement = 0.001 if isFloat else 1

        singleChooser = self.getSingleChooser()
        self.x = singleChooser(self, "x", a, isFloat, self.FireEvent, minCrement)
        self.y = singleChooser(self, "y", b, isFloat, self.FireEvent, minCrement)
        self.w = singleChooser(self, "w", c, isFloat, self.FireEvent, minCrement)
        self.h = singleChooser(self, "h", d, isFloat, self.FireEvent, minCrement)

        self.check = tryGetFloat if isFloat else tryGetInt
        self.subclassLayout()

    def getSingleChooser(self):
        return NumberChooser

    def subclassLayout(self):
        self.x.grid(row=1, column=0)
        self.y.grid(row=1, column=1)
        self.w.grid(row=1, column=2)
        self.h.grid(row=1, column=3)

    def FireEvent(self, _):
        # convert from string to integer
        x = self.check(self.x.value.get())
        y = self.check(self.y.value.get())
        w = self.check(self.w.value.get())
        h = self.check(self.h.value.get())
        if x[0] and y[0] and w[0] and h[0]:
            self.OnChange([item[1] for item in [x, y, w, h]])

    def show(self, value):
        x, y, w, h = value
        self.x.value.set(str(x))
        self.y.value.set(str(y))
        self.w.value.set(str(w))
        self.h.value.set(str(h))


class CompactRectChooser(RectChooser):
    def subclassLayout(self):
        self.x.grid(row=1, column=0)
        self.y.grid(row=2, column=0)
        self.w.grid(row=3, column=0)
        self.h.grid(row=4, column=0)

    def getSingleChooser(self):
        return CompactNumberChooser
