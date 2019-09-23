import tkinter as tk
from PIL import ImageTk


class ImageCanvas(tk.Canvas):

    def __init__(self, root):
        super().__init__(root, width=512, height=480)        
        self._getImg = None
        self._img = None
        
        self.ph = None        

    def update(self):
        if self._getImg is not None: 
            self.updateImage(self._getImg())
            
    def updateImage(self, image):        
        if image is not None:            
            self.ph = ImageTk.PhotoImage(image)
            
            # create image if not existing...
            if self._img is None:
                borderSize = self.cget('bd')
                self._img = self.create_image(borderSize, borderSize, image=self.ph,anchor=tk.NW)
            else:    
                self._img = self.itemconfig(self._img, image=self.ph)                        
        
    def SetImageSource(self, callback):
        self._getImg = callback
