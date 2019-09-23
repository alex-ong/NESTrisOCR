import tkinter as tk
from PIL import Image, ImageDraw
from lib import *
from OCRAlgo.PieceStatsTextOCR import generate_stats
from calibration.StringChooser import StringChooser
from calibration.RectChooser import RectChooser
from calibration.ImageCanvas import ImageCanvas

class Calibrator(tk.Frame):
            
    def __init__(self, config):
        self.config = config
        root = tk.Tk()
        super().__init__(root)
        root.protocol("WM_DELETE_WINDOW", self.on_exit)
        root.focus_force()             
        root.wm_title("NESTrisOCR calibrator")
        self.pack()
        self.root = root
        self.destroying = False    
        root.config(background="black")
        StringChooser(self,"capture window starts with:", config.WINDOW_NAME, config.setWindowName, 20).grid(sticky='nsew')
        StringChooser(self,"player name",config.player_name, config.setPlayerName,25).grid(sticky='nsew')
        #StringChooser(self,"multi_thread",config.multi_thread, config.set,25).grid(sticky='nsew')
        #StringChooser(self,"player name",config.player_name, config.setPlayerName,25).grid(sticky='nsew')
        
        # window coords
        r = RectChooser(self,"capture window coords (pixels)", config.CAPTURE_COORDS,False, self.updateWindowCoords)
        r.config(relief=tk.FLAT,bd=5,background='orange')
        r.grid()
        
        self.boardImage = ImageCanvas(self)
        self.boardImage.config(relief=tk.FLAT,bd=5,background='orange')
        self.boardImage.grid()
        self.boardImage.SetImageSource(lambda: draw_calibration(self.config))
        self.boardImage.update()
    
    def updateWindowCoords(self, result):
        x,y,w,h = result
        self.config.setGameCoords(result)
        self.boardImage.update()

    def update(self):        
        if not self.destroying:
            super().update()
    
    def on_exit(self):                
        self.destroying = True
        self.root.destroy()
        


def highlight_calibration(img, c):    
    poly = Image.new('RGBA', (img.width,img.height))
    draw = ImageDraw.Draw(poly)
    
    red = (255,0,0,128)    
    blue = (0,0,255,128)       
    orange = (255,165,0,128)
    
    scorePerc, linesPerc, levelPerc = (c.scorePerc, c.linesPerc, c.levelPerc)
    #score
    draw.rectangle(screenPercToPixels(img.width,img.height,scorePerc),fill=red)
    #lines
    draw.rectangle(screenPercToPixels(img.width,img.height,linesPerc),fill=red)
    #level
    draw.rectangle(screenPercToPixels(img.width,img.height,levelPerc),fill=red)    
    if c.capture_stats:
        if c.stats_method == 'TEXT':
            #pieces
            draw.rectangle(screenPercToPixels(img.width,img.height,c.statsPerc),fill=blue)
            for value in generate_stats(c.CAPTURE_COORDS,c.statsPerc,c.scorePerc[3],False).values():
                draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
        else: #c.stats_method == 'FIELD':
            stats2Perc = c.stats2Perc
            draw.rectangle(screenPercToPixels(img.width,img.height,stats2Perc),fill=blue)
            for x in range(4):
                for y in range(2):                
                    blockPercX = lerp(stats2Perc[0], stats2Perc[0] + stats2Perc[2], x / 4.0 + 1 / 8.0)
                    blockPercY = lerp(stats2Perc[1], stats2Perc[1] + stats2Perc[3], y / 2.0 + 1 / 4.0)
                    rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
                    draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
        
        img.paste(poly,mask=poly)    
    del draw

#todo, return image or array of images with cropped out sections.    
def draw_calibration(config):
    hwnd = getWindow()
    if hwnd is None:
        print("Unable to find window with title:",  config.WINDOW_NAME)
        return None
    
    img = WindowCapture.ImageCapture(config.CAPTURE_COORDS, hwnd)
    highlight_calibration(img, config)   
    img.thumbnail((512,480),Image.NEAREST)
    return img
    