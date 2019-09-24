import tkinter as tk
from PIL import Image, ImageDraw
from lib import *
from OCRAlgo.PieceStatsTextOCR import generate_stats
from calibration.StringChooser import StringChooser
from calibration.RectChooser import RectChooser, CompactRectChooser
from calibration.ImageCanvas import ImageCanvas
from calibration.draw_calibration import draw_calibration
from calibration.OtherOptions import create_window

UPSCALE=4
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
        StringChooser(self,"capture window starts with:", config.WINDOW_NAME, config.setWindowName, 20).grid(row=0,sticky='nsew')
        StringChooser(self,"player name",config.player_name, config.setPlayerName,25).grid(row=1,sticky='nsew')
        tk.Button(self,text="Other options", command=lambda: create_window(root, self.config)).grid(row=0,column=1)
        
        # window coords
        r = RectChooser(self,"capture window coords (pixels)", config.CAPTURE_COORDS,False, self.updateWindowCoords)
        r.config(relief=tk.FLAT,bd=5,background='orange')
        r.grid(row=2)
        
        border = tk.Frame(self)
        border.grid(row=3,rowspan=10)
        border.config(relief=tk.FLAT,bd=5,background='orange')
        self.boardImage = ImageCanvas(border,512,480)        
        self.boardImage.pack()
        
        canvasSize = pixelSize(6,UPSCALE)
        CompactRectChooser(self,"lines (imagePerc)",config.linesPerc,True,self.updateLinesPerc).grid(row=3,column=1)
        self.linesImage = ImageCanvas(self,canvasSize[0],canvasSize[1])        
        self.linesImage.grid(row=4,column=1)
        
        CompactRectChooser(self,"score (imagePerc)", config.scorePerc,True,self.updateScorePerc).grid(row=5,column=1)
        self.scoreImage = ImageCanvas(self,canvasSize[0],canvasSize[1])        
        self.scoreImage.grid(row=6,column=1)

        CompactRectChooser(self,"level (imagePerc)", config.levelPerc,True,self.updateLevelPerc).grid(row=7,column=1)
        self.levelImage = ImageCanvas(self,canvasSize[0],canvasSize[1])        
        self.levelImage.grid(row=8,column=1)

        self.redrawImages()

    def updateLinesPerc(self, result):
        self.config.setLinesPerc(result)
        self.redrawImages()
    
    def updateScorePerc(self, result):
        self.config.setScorePerc(result)
        self.redrawImages()
    
    def updateLevelPerc(self, result):
        self.config.setLevelPerc(result)
        self.redrawImages()

    def updateWindowCoords(self, result):
        self.config.setGameCoords(result)
        self.redrawImages()

    def redrawImages(self):
        board = self.getNewBoardImage()
        if board is None:
            return
        dim = board.width, board.height        
        
        lines_img = board.crop(pixelPercRect(dim, self.config.linesPerc))        
        lines_img = lines_img.resize(pixelSize(3,4),Image.ANTIALIAS)

        score_img = board.crop(pixelPercRect(dim, self.config.scorePerc))        
        score_img = score_img.resize(pixelSize(6,4),Image.ANTIALIAS)

        level_img = board.crop(pixelPercRect(dim, self.config.levelPerc))        
        level_img = level_img.resize(pixelSize(2,4),Image.ANTIALIAS)

        self.boardImage.updateImage(board)
        self.linesImage.updateImage(lines_img)
        self.scoreImage.updateImage(score_img)
        self.levelImage.updateImage(level_img)
    
    def getNewBoardImage(self):
        return draw_calibration(self.config)

    def update(self):        
        if not self.destroying:
            super().update()
    
    def on_exit(self):                
        self.destroying = True
        self.root.destroy()
        
def pixelSize(numDigits, upscale):
    return ((7 * numDigits + numDigits-1) * upscale, 
             7 * upscale)

#sources: PixelDimensions (w,h), RectPerc(x,y,w,h)
#out: RectPixel(x,y,x2,y2)
def pixelPercRect(dim,rectPerc):
    x1 = round(dim[0] * rectPerc[0])
    y1 = round(dim[1] * rectPerc[1])
    x2 = round(x1 + dim[0]*rectPerc[2])
    y2 = round(y1 + dim[1]*rectPerc[3])
    return (x1,y1,x2,y2)
