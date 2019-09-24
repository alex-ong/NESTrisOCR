import tkinter as tk

class OptionChooser(tk.Frame):
    def __init__(self, master, name, itemsRaw, itemsStr, default, onChange):
        super().__init__(master)
        tk.Label(self,text=name).pack(side=tk.LEFT,fill='both')
        self.stringVar = tk.StringVar()
        
        try:     
            index = itemsRaw.index(default)
        except ValueError:
            index = 0

        self.stringVar.set(itemsStr[index])
        self.itemIndex = index
        
        self.mapping = {}
        #there has got to be a pythonic way of doing this:
        for i, string in enumerate(itemsStr):
            self.mapping[string] = itemsRaw[i]

        self.itemsRaw = itemsRaw
        self.itemsStr = itemsStr
        self.onChange = onChange
        self.optionMenu = tk.OptionMenu(self,self.stringVar, *itemsStr, command=self.valChanged)
        self.optionMenu.pack(side=tk.RIGHT,fill='both')
    
    def valChanged(self, i):        
        rawItem = self.mapping[self.stringVar.get()]
        self.onChange(rawItem)