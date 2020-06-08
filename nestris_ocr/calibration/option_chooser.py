import tkinter as tk


class OptionChooser(tk.Frame):
    def __init__(self, master, name, itemsRaw, itemsStr, default, onChange):
        super().__init__(master)
        tk.Label(self, text=name).pack(side=tk.LEFT, fill="both")
        self.stringVar = tk.StringVar()

        try:
            index = itemsRaw.index(default)
        except ValueError:
            index = 0

        self.stringVar.set(itemsStr[index])
        self.itemIndex = index

        # https://stackoverflow.com/questions/209840/convert-two-lists-into-a-dictionary
        self.mapping = dict(zip(itemsStr, itemsRaw))

        self.itemsRaw = itemsRaw
        self.itemsStr = itemsStr
        self.onChange = onChange
        self.optionMenu = tk.OptionMenu(
            self, self.stringVar, *itemsStr, command=self.valChanged
        )
        self.optionMenu.pack(side=tk.RIGHT, fill="both")

    def valChanged(self, i):
        rawItem = self.mapping[self.stringVar.get()]
        self.onChange(rawItem)

    def refresh(self, value):
        self.stringVar.set(value)
