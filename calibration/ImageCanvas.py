import tkinter as tk
from PIL import ImageTk


class ImageCanvas(tk.Canvas):

    def __init__(self, root, width, height):
        super().__init__(root, width=width, height=height)        
        self._getImg = None
        self._img = None
        
        self.ph = None        
        
    def updateImage(self, image):        
        if image is not None:            
            self.ph = ImageTk.PhotoImage(image)
            
            # create image if not existing...
            if self._img is None:
                self._img = self.create_image(0, 0, image=self.ph,anchor=tk.NW)
            else:
                self._img = self.itemconfig(self._img, image=self.ph)

        
