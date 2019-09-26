import tkinter as tk
import multiprocessing
from calibration.OptionChooser import OptionChooser
from calibration.BoolChooser import BoolChooser
from calibration.Presets import presets

INSTANCE = None
 
class OtherOptions(tk.Toplevel):
    def __init__(self, root, config, on_destroy):
        super().__init__(root)
        self.config = config
        self.on_destroy = on_destroy
        #presets
        items = list(presets.keys())
        self.presets = OptionChooser(self,'Choose preset', items,items,"",self.changePreset)

        #multiprocessing
        items = [i + 1 for i in range(multiprocessing.cpu_count())]
        itemsStr = [str(item) for item in items]        
        self.mt = OptionChooser(self,'Use multi_thread', items, itemsStr, 
                      config.threads, self.changeMultiThread)        
        #hexSupport
        self.hex = BoolChooser(self,'Support hex scores (scores past 999999 as A00000 to F99999)',
                    config.hexSupport,self.changeHexSupport)
        #captureField
        self.fieldCap = BoolChooser(self,'Capture game field',
                                    config.capture_field,self.changeCaptureField)
        
        #capturePreview
        self.prevCap = BoolChooser(self,'Capture next piece',
                                   config.capture_preview,self.changeCapturePreview)

        #captureStats
        self.statCap = BoolChooser(self,'Capture Piece Stats', config.capture_stats, 
                                   self.changeCaptureStats)

        self.statsMethod = OptionChooser(self,'Piece Stats capture method',
                                         ['TEXT','FIELD'],['TEXT','FIELD'],
                                         config.stats_method,self.changeStatsMethod)
        
        self.presets.pack(fill='both')
        self.mt.pack(fill='both')
        self.hex.pack(fill='both')
        self.fieldCap.pack(fill='both')
        self.prevCap.pack(fill='both')
        self.statCap.pack(fill='both')
        if config.capture_stats:
            self.statsMethod.pack(fill='both')

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.wm_title("NESTrisOCR Options")
        self.grab_set()

    def changePreset(self, value):
        presets[value](self.config)
        self.refreshValues()

    def refreshValues(self):
        self.mt.refresh(self.config.threads)
        self.hex.refresh(self.config.hexSupport)
        self.fieldCap.refresh(self.config.capture_field)
        self.prevCap.refresh(self.config.capture_preview)
        self.statCap.refresh(self.config.capture_stats)
        self.statsMethod.refresh(self.config.stats_method)
        self.showHideStatsMethod()

    def changeMultiThread(self, value):
        self.config.setThreads(value)
    
    def changeHexSupport(self, value):        
        self.config.setHexSupport(value)
    
    def changeCaptureField(self, value):        
        self.config.setCaptureField(value)
    
    def changeCapturePreview(self, value):        
        self.config.setCapturePreview(value)

    def showHideStatsMethod(self):
        if self.config.capture_stats:                    
            self.statsMethod.pack(fill='both')
        else:
            self.statsMethod.pack_forget()
    def changeCaptureStats(self,value):
        self.config.setCaptureStats(value)
        self.showHideStatsMethod()
    
    def changeStatsMethod(self, value):
        self.config.setStatsMethod(value)

    def on_exit(self):        
        global INSTANCE
        INSTANCE = None
        self.on_destroy()
        self.destroy()

def create_window(root, config, on_destroy):
    global INSTANCE
    if INSTANCE is None:    
        INSTANCE = OtherOptions(root,config,on_destroy)
    
