import tkinter as tk
from nestris_ocr.calibration.string_chooser import StringChooser
from nestris_ocr.calibration.option_chooser import OptionChooser

from nestris_ocr.capturing.opencv.list_devices import get_device_list

MODES = ["OPENCV", "WINDOW", "OPENCV", "FILE"]
MODES_DISPLAY = ["CAPTURE CARD", "WINDOW", "RTMP", "FILE"]


class CaptureMethod(tk.Frame):
    def __init__(self, master, default, onChangeArray):
        super().__init__(master)
        self.modes = MODES
        self.modes_display = MODES_DISPLAY
        display_mode = self.raw_mode_to_display(default[0], default[1])
        self.option_chooser = OptionChooser(
            self,
            "What are you capturing from",
            MODES_DISPLAY,
            MODES_DISPLAY,
            display_mode,
            self.mode_changed,
        )

        self.mode_mapping = dict(
            zip(self.modes_display, self.modes)
        )  # maps "CAPTURE CARD" to "OPENCV"
        self.option_chooser.pack(fill=tk.BOTH)
        self.onChangeMode = onChangeArray[0]

        self.manual_source_id = StringChooser(
            self,
            "Window name starts with...",
            default[1],
            self.source_id_changed,
            100,  # source ids can be local file or openCV stream URLs
        )

        self.device_mapping = get_device_list()

        self.auto_source_id = OptionChooser(
            self,
            "Which capture card?",
            list(self.device_mapping.keys()),
            list(self.device_mapping.values()),
            self.source_id_to_int(default[1]),
            self.source_id_changed,
        )

        self.on_change_source_id = onChangeArray[1]
        self.change_source_id_silent = onChangeArray[2]
        self.enable_choose_source_id(display_mode)

    def source_id_to_int(self, string: str) -> int:
        try:
            return int(string)
        except ValueError:
            return 0

    def raw_mode_to_display(self, mode, source_id):
        if mode == "OPENCV":
            try:
                int(source_id)
                return "CAPTURE CARD"
            except ValueError:
                return "RTMP"
        else:
            return mode

    def enable_choose_source_id(self, mode_display):
        self.silent_source_id = True
        if mode_display == "CAPTURE CARD":
            self.manual_source_id.pack_forget()
            self.auto_source_id.pack(fill=tk.BOTH)
            self.auto_source_id.valChanged(None)  # refresh config.
        else:
            self.auto_source_id.pack_forget()
            self.manual_source_id.pack(fill=tk.BOTH)
            self.manual_source_id.changeValueText()  # refresh config.
        self.silent_source_id = False

    def mode_changed(self, option):
        self.enable_choose_source_id(option)
        self.onChangeMode(self.mode_mapping[option])

    def source_id_changed(self, value):
        value = str(value)
        if self.silent_source_id:
            self.change_source_id_silent(value)
        else:
            self.on_change_source_id(value)

    def refresh(self, value):
        self.modeVar.set(value)
