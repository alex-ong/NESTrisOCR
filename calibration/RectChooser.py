import tkinter as tk
from calibration.NumberChooser import NumberChooser

from lib import tryGetInt

        
class RectChooser(tk.Frame):

    def __init__(self, root, name, defaultValue, isFloat, OnChange):
        super().__init__(root)        
        self.OnChange = OnChange
        a,b,c,d = defaultValue        

        tk.Label(self,text=name).grid(row=0,columnspan=4,sticky='nsew')

        self.x = NumberChooser(self, 'x', a, isFloat, self.FireEvent, 1)
        self.y = NumberChooser(self, 'y', b, isFloat, self.FireEvent, 1)
        self.w = NumberChooser(self, 'w', c, isFloat, self.FireEvent, 1)
        self.h = NumberChooser(self, 'h', d, isFloat, self.FireEvent, 1)
        
        self.x.grid(row=1, column=0)
        self.y.grid(row=1, column=1)
        self.w.grid(row=1, column=2)
        self.h.grid(row=1, column=3)

    def FireEvent(self, _):   
        # convert from string to integer
        x = tryGetInt(self.x.value.get())
        y = tryGetInt(self.y.value.get())
        w = tryGetInt(self.w.value.get())
        h = tryGetInt(self.h.value.get())
        if (x[0] and y[0] and w[0] and h[0]):
            self.OnChange([item[1] for item in [x, y, w, h]])

    def show(self, value):
        x, y, w, h = value
        self.x.value.set(str(x))
        self.y.value.set(str(y))
        self.w.value.set(str(w))
        self.h.value.set(str(h))
        
        
