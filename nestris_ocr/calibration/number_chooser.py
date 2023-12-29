import tkinter as tk

from nestris_ocr.calibration.widgets import Button
from nestris_ocr.utils.lib import tryGetFloat, tryGetInt


class NumberChooser(tk.Frame):
    def __init__(self, root, name, defaultValue, isFloat, OnChange, minCrement):
        super().__init__(root)
        self.isFloat = isFloat
        self.value = tk.StringVar()
        self.value.set(str(defaultValue))
        self.value.trace("w", lambda name, index, mode: self.changeValueText())
        self.OnChange = OnChange
        self.checker = tryGetFloat if self.isFloat else tryGetInt
        self.config(bd=1, relief=tk.RAISED)

        f = tk.Frame(self)
        # row 1
        f.grid(row=0, column=0, columnspan=4)
        tk.Label(f, text=name).grid(row=0, column=0)
        tk.Entry(f, textvariable=self.value, width=5).grid(row=0, column=1)
        # row 2
        Button(
            self, text="--", width=2, command=lambda: self.changeValue(-minCrement * 10)
        ).grid(row=1, column=0, sticky="nsew")
        Button(
            self, text="-", width=2, command=lambda: self.changeValue(-minCrement)
        ).grid(row=1, column=1, sticky="nsew")
        Button(
            self, text="+", width=2, command=lambda: self.changeValue(+minCrement)
        ).grid(row=1, column=2, sticky="nsew")
        Button(
            self, text="++", width=2, command=lambda: self.changeValue(+minCrement * 10)
        ).grid(row=1, column=3, sticky="nsew")

    def changeValueText(self):
        success, value = self.checker(self.value.get())
        if success:
            self.OnChange(value)

    def changeValue(self, amount):
        success, value = self.checker(self.value.get())
        if success:
            value += amount
            self.value.set(str(value))
        # self.OnChange()


class CompactNumberChooser(tk.Frame):
    def __init__(self, root, name, defaultValue, isFloat, OnChange, minCrement):
        super().__init__(root)
        self.isFloat = isFloat
        self.value = tk.StringVar()
        self.value.set(str(defaultValue))
        self.value.trace("w", lambda name, index, mode: self.changeValueText())
        self.OnChange = OnChange
        self.checker = tryGetFloat if self.isFloat else tryGetInt
        self.config(bd=1, relief=tk.RAISED)
        tk.Label(self, text=name).grid(row=0, column=0)
        tk.Entry(self, textvariable=self.value, width=5).grid(row=0, column=1)
        Button(
            self, text="--", width=2, command=lambda: self.changeValue(-minCrement * 10)
        ).grid(row=0, column=2, sticky="nsew")
        Button(
            self, text="-", width=2, command=lambda: self.changeValue(-minCrement)
        ).grid(row=0, column=3, sticky="nsew")
        Button(
            self, text="+", width=2, command=lambda: self.changeValue(+minCrement)
        ).grid(row=0, column=4, sticky="nsew")
        Button(
            self, text="++", width=2, command=lambda: self.changeValue(+minCrement * 10)
        ).grid(row=0, column=5, sticky="nsew")

    def changeValueText(self):
        success, value = self.checker(self.value.get())
        if success:
            self.OnChange(value)

    def changeValue(self, amount):
        success, value = self.checker(self.value.get())
        if success:
            value += amount
            self.value.set(str(value))
        # self.OnChange()
