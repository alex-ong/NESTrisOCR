import tkinter as tk
class StringChooser(tk.Frame):
    def __init__(self, root, name, defaultValue, OnChange, maxLength):
        super().__init__(root)
        self.value = tk.StringVar()
        self.value.set(defaultValue)
        self.maxLength = maxLength
        self.value.trace("w", lambda name, index, mode: self.changeValueText())
        self.OnChange = OnChange
        self.lastValue = defaultValue
        tk.Label(self,text=name).pack(side=tk.LEFT)
        tk.Entry(self,textvariable=self.value).pack(side=tk.RIGHT)

    def changeValueText(self):
        success = len(self.value.get()) < self.maxLength
        for item in self.value.get():
            if item not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRUSTUVWXYZ-_1234567890':
                success = False
        if success:
            self.OnChange(self.value.get())
            self.lastValue = self.value.get()
        else:
            self.value.set(self.lastValue)
        
    def changeValue(self, amount):
        success, value = tryGetFloat(self.value.get())
        if success:
            value += amount
            self.value.set(str(value))
