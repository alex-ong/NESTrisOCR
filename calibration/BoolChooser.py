import tkinter as tk

class BoolChooser(tk.Frame):
    def __init__(self, master, name, default, onChange):
        super().__init__(master)
        tk.Label(self,text=name).pack(side=tk.LEFT,fill='both')
        self.boolVar = tk.BooleanVar()        
        self.boolVar.set(default)
        
        self.onChange = onChange
        self.checkBox = tk.Checkbutton(self,variable=self.boolVar,command=self.valChanged)
        self.checkBox.pack(side=tk.RIGHT,fill='both')
    
    def valChanged(self):        
        rawItem = self.boolVar.get()
        self.onChange(rawItem)
    
    def refresh(self, value):
        self.boolVar.set(value)