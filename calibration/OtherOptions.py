import tkinter as tk
import multiprocessing
from calibration.OptionChooser import OptionChooser

INSTANCE = None
 
class OtherOptions(tk.Toplevel):
    def __init__(self, root, config):
        super().__init__(root)
        self.config = config

        #multiprocessing
        items = [i+1 for i in range(multiprocessing.cpu_count())]
        itemsStr = [str(item) for item in items]        
        mt = OptionChooser(self,'Use multi_thread', items, itemsStr, config.threads, self.changeMultiThread).pack()        

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.wm_title("NESTrisOCR Options")

    def changeMultiThread(self, value):
        self.config.setThreads(value)

    def on_exit(self):        
        global INSTANCE
        INSTANCE = None
        self.destroy()

def create_window(root, config):
    global INSTANCE
    if INSTANCE is None:    
        INSTANCE = OtherOptions(root,config)
    
