import tkinter as tk
from lib import tryGetFloat
from lib import tryGetInt

class NumberChooser(tk.Frame):
    def __init__(self, root, name, defaultValue, isFloat, OnChange, minCrement):
        super().__init__(root)
        self.isFloat = isFloat
        self.value = tk.StringVar()
        self.value.set(str(defaultValue))
        self.value.trace("w", lambda name, index, mode: self.changeValueText())
        self.OnChange = OnChange
        self.checker = tryGetFloat if self.isFloat else tryGetInt
        self.config(bd=1,relief=tk.RAISED)
        tk.Label(self,text=name).grid(row=0,column=0)
        tk.Entry(self,textvariable=self.value,width=5).grid(row=0,column=1,columnspan=1)
        tk.Button(self,text='--',width=2,command=lambda:self.changeValue(-minCrement*10)).grid(row=1,column=0,sticky='nsew')
        tk.Button(self,text='-',width=2,command=lambda:self.changeValue(-minCrement)).grid(row=1,column=1,sticky='nsew')
        tk.Button(self,text='+',width=2,command=lambda:self.changeValue(+minCrement)).grid(row=1,column=2,sticky='nsew')
        tk.Button(self,text='++',width=2,command=lambda:self.changeValue(+minCrement*10)).grid(row=1,column=3,sticky='nsew')
    
    def changeValueText(self):
        
        success, value = self.checker(self.value.get())
        if success:
            self.OnChange(value)
        
    def changeValue(self, amount):
        success, value = self.checker(self.value.get())
        if success:
            value += amount
            self.value.set(str(value))
        #self.OnChange()    