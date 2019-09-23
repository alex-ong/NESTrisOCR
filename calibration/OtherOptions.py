import tkinter as tk

INSTANCE = None
 
class OtherOptions(tk.Toplevel):
    def __init__(self, root, config):
        print("one")
        super().__init__(root)
        self.config = config
        tk.Label(self,text='testerino').pack()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.wm_title("NESTrisOCR Options")

    def on_exit(self):
        print('exiting')
        global INSTANCE
        INSTANCE = None
        self.destroy()

def create_window(root, config):
    global INSTANCE
    if INSTANCE is None:
        print("two")
        INSTANCE = OtherOptions(root,config)
    else:
        print("three")
