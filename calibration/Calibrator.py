import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageDraw
from lib import *
from OCRAlgo.PieceStatsTextOCR import generate_stats
from calibration.StringChooser import StringChooser
from calibration.RectChooser import RectChooser, CompactRectChooser
from calibration.ImageCanvas import ImageCanvas
from calibration.draw_calibration import draw_calibration
from calibration.OtherOptions import create_window
from calibration.auto_calibrate import auto_calibrate_raw

import time
UPSCALE = 4
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
        StringChooser(self,"capture window starts with:", config.WINDOW_NAME, self.updateWindowName, 20).grid(row=0,sticky='nsew')
        StringChooser(self,"player name",config.player_name, config.setPlayerName,25).grid(row=1,sticky='nsew')
        tk.Button(self,text="Other options", 
                  command=lambda: create_window(root, self.config,self.otherOptionsClosed)).grid(row=0,column=1)
        
        # window coords
        r = RectChooser(self,"capture window coords (pixels)", config.CAPTURE_COORDS,False, self.updateWindowCoords)
        r.config(relief=tk.FLAT,bd=5,background='orange')
        r.grid(row=2)
        self.winCoords = r
        
        # auto calibrate
        border = tk.Frame(self)
        border.config(relief=tk.FLAT,bd=5,background='orange')
        border.grid(row=2,column=1,sticky='nsew')

        autoCalibrate = tk.Button(border,text="Automatically detect field", 
                                  command=self.autoDetectField)        
        autoCalibrate.pack(fill='both',expand=True)

        border = tk.Frame(self)
        border.grid(row=3,column=0,stick='nsew')
        border.config(relief=tk.FLAT,bd=5,background='orange')
        self.boardImage = ImageCanvas(border,512,224 * 2)        
        self.boardImage.pack()
        
        self.tabManager = ttk.Notebook(self)
        self.tabManager.grid(row=3,column=1,sticky='nsew')

        self.setupTab1()
        self.setupTab2()

        self.redrawImages()
        self.lastUpdate = time.time()
    
    def setupTab1(self):
        f = tk.Frame(self.tabManager)
        canvasSize = pixelSize(6,UPSCALE)
        CompactRectChooser(f,"lines (imagePerc)",config.linesPerc,True,self.updateLinesPerc).grid()
        self.linesImage = ImageCanvas(f,canvasSize[0],canvasSize[1])        
        self.linesImage.grid()
        
        CompactRectChooser(f,"score (imagePerc)", config.scorePerc,True,self.updateScorePerc).grid()
        self.scoreImage = ImageCanvas(f,canvasSize[0],canvasSize[1])        
        self.scoreImage.grid()

        CompactRectChooser(f,"level (imagePerc)", config.levelPerc,True,self.updateLevelPerc).grid()
        self.levelImage = ImageCanvas(f,canvasSize[0],canvasSize[1])        
        self.levelImage.grid()
        self.tabManager.add(f,text="NumberOCR")
    
    def setupTab2(self):
        f = tk.Frame(self.tabManager)        
        a = CompactRectChooser(f,"field (imagePerc)",config.fieldPerc,True,self.updateFieldPerc)        
        b = CompactRectChooser(f,"Color1 (imagePerc)",config.color1Perc,True,self.updateColor1Perc)
        c = CompactRectChooser(f,"Color2 (imagePerc)",config.color2Perc,True,self.updateColor2Perc)
        self.fieldCaptures = [a,b,c]
        self.pieceStats = CompactRectChooser(f,"pieceStats (imagePerc)",config.statsPerc,True,self.updateStatsPerc)
        a.grid()
        b.grid()
        c.grid()
        self.pieceStats.grid()
        self.setFieldTextVisible()
        self.setStatsTextVisible()
        self.tabManager.add(f,text="FieldStats")
    
    def setFieldTextVisible(self):
        show = False
        if (self.config.capture_field or 
           (self.config.capture_stats and self.config.stats_method == 'FIELD')):
               show = True

        for item in self.fieldCaptures:
            if show:
                item.grid()
            else:
                item.grid_forget()

    def setStatsTextVisible(self):
        if self.config.capture_stats and self.config.stats_method == 'TEXT':
            self.pieceStats.grid()
        else:
            self.pieceStats.grid_forget()

    def getActiveTab(self):
        return self.tabManager.index(self.tabManager.select())

    def updateRedraw(self, func, result):
        func(result)
        self.redrawImages()

    def updateWindowName(self, result):
        self.updateRedraw(self.config.setWindowName,result)

    def updateLinesPerc(self, result):
        self.updateRedraw(self.config.setLinesPerc, result)        
    
    def updateScorePerc(self, result):
        self.updateRedraw(self.config.setScorePerc, result)
    
    def updateLevelPerc(self, result):
        self.updateRedraw(self.config.setLevelPerc, result)
    
    def updateLevelPerc(self, result):
        self.updateRedraw(self.config.setLevelPerc, result)

    def updateWindowCoords(self, result):
        self.updateRedraw(self.config.setGameCoords, result)
    
    def updateFieldPerc(self, result):
        self.updateRedraw(self.config.setFieldPerc, result)
    
    def updateColor1Perc(self, result):
        self.updateRedraw(self.config.setColor1Perc, result)
    
    def updateColor2Perc(self, result):
        self.updateRedraw(self.config.setColor2Perc, result)
    
    def updateStatsPerc(self, result):
        self.updateRedraw(self.config.setStatsPerc, result)

    def redrawImages(self):
        self.lastUpdate = time.time()
        board = self.getNewBoardImage()
        if board is None:
            self.noBoard = True
            return 
        else:
            self.noBoard = False

        dim = board.width, board.height        
        
        self.boardImage.updateImage(board)

        if self.getActiveTab() == 0:
            lines_img = board.crop(pixelPercRect(dim, self.config.linesPerc))        
            lines_img = lines_img.resize(pixelSize(3,4),Image.ANTIALIAS)

            score_img = board.crop(pixelPercRect(dim, self.config.scorePerc))        
            score_img = score_img.resize(pixelSize(6,4),Image.ANTIALIAS)

            level_img = board.crop(pixelPercRect(dim, self.config.levelPerc))        
            level_img = level_img.resize(pixelSize(2,4),Image.ANTIALIAS)
            self.linesImage.updateImage(lines_img)
            self.scoreImage.updateImage(score_img)
            self.levelImage.updateImage(level_img)

    def getNewBoardImage(self):
        return draw_calibration(self.config)

    def autoDetectField(self):
        rect = auto_calibrate_raw(self.config)
        if rect is not None:            
            self.winCoords.show(rect)

    def update(self):        
        if not self.destroying:
            if (time.time() - self.lastUpdate > 5.0 and self.noBoard):
                self.redrawImages()
            super().update()
    
    def otherOptionsClosed(self):
        self.redrawImages()
        self.setStatsTextVisible()
        self.setFieldTextVisible()

    def on_exit(self):                
        self.destroying = True
        self.root.destroy()
        
def pixelSize(numDigits, upscale):
    return ((7 * numDigits + numDigits - 1) * upscale, 
             7 * upscale)

#sources: PixelDimensions (w,h), RectPerc(x,y,w,h)
#out: RectPixel(x,y,x2,y2)
def pixelPercRect(dim,rectPerc):
    x1 = round(dim[0] * rectPerc[0])
    y1 = round(dim[1] * rectPerc[1])
    x2 = round(x1 + dim[0] * rectPerc[2])
    y2 = round(y1 + dim[1] * rectPerc[3])
    return (x1,y1,x2,y2)
