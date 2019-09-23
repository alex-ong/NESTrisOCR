import tkinter as tk
from lib import tryGetFloat
class NumberChooser(tk.Frame):
    def __init__(self, root, name, OnChange, minCrement):
        super().__init__(root)
        self.value = tk.StringVar()
        
        self.value.trace("w", lambda name, index, mode: self.changeValueText())
        self.OnChange = OnChange
        tk.Label(self,text=name).grid(row=0,columnspan=4)
        tk.Entry(self,textvariable=self.value).grid(row=1,columnspan=4)
        tk.Button(self,text='--',command=lambda:self.changeValue(-minCrement*10)).grid(row=2,column=0)
        tk.Button(self,text='-',command=lambda:self.changeValue(-minCrement)).grid(row=2,column=1)
        tk.Button(self,text='+',command=lambda:self.changeValue(+minCrement)).grid(row=2,column=2)
        tk.Button(self,text='++',command=lambda:self.changeValue(+minCrement*10)).grid(row=2,column=3)
    
    def changeValueText(self):
        success, _ = tryGetFloat(self.value.get())
        if success:
            self.OnChange()
        
    def changeValue(self, amount):
        success, value = tryGetFloat(self.value.get())
        if success:
            value += amount
            self.value.set(str(value))
        #self.OnChange()    