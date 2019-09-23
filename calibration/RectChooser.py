import tkinter as tk
from NumberChooser import NumberChooser

from lib import tryGetInt

        
class RectChooser(tk.Frame):

    def __init__(self, root, OnChange):
        super().__init__(root)        
        self.OnChange = OnChange
        
        self.x = NumberChooser(self, 'x', self.FireEvent, 1)
        self.y = NumberChooser(self, 'y', self.FireEvent, 1)
        self.w = NumberChooser(self, 'w', self.FireEvent, 1)
        self.h = NumberChooser(self, 'h', self.FireEvent, 1)
    
        self.x.grid(row=0, column=0)
        self.y.grid(row=0, column=1)
        self.w.grid(row=0, column=2)
        self.h.grid(row=0, column=3)

    def FireEvent(self):   
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
        
        
