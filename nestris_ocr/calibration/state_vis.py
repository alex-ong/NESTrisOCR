from nestris_ocr.calibration.field_view import FieldView, sample_data
import tkinter as tk
import numpy as np

class ValueLabel(tk.Frame):
    def __init__(self, master, name):
        super().__init__(master)
        nameLabel = tk.Label(self, text=name)
        nameLabel.pack(side=tk.LEFT)
        self.value = tk.Label(self, text='')
        self.value.pack(side=tk.RIGHT)

    def updateValue(self, value):
        self.value['text'] = str(value)

class StateVisualizer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.score = ValueLabel(self, "Score")
        self.lines = ValueLabel(self, "Lines")
        self.level = ValueLabel(self, "Level")

        self.field = FieldView(self, 100, 200)

        self.field.grid(row=0,column=0,rowspan=5)
        self.score.grid(row=0,column=1)
        self.lines.grid(row=1,column=1)
        self.level.grid(row=2,column=1)
        self.updateValues(self.dummy_data())
    
    def dummy_data(self):
        field = np
        return {
                "score": None,
                "lines": None,
                "level": None,
                "field": sample_data() #np.ones((20,10),dtype=np.uint8)
                }

    def updateValues(self, values):
        self.score.updateValue(values["score"])
        self.lines.updateValue(values["lines"])
        self.level.updateValue(values["level"])
        self.field.updateField(values["field"], values["level"])

