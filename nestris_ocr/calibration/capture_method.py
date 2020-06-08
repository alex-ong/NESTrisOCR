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
            self.manual_entry_changed,
            100,  # source ids can be local file or openCV stream URLs
        )

        devices = get_device_list()
        self.device_mapping = dict(devices)

        self.auto_source_id = OptionChooser(
            self,
            "Which capture card?",
            [d[0] for d in devices],
            [d[1] for d in devices],
            default[1],
            self.capture_device_changed,
        )

        self.on_change_source_id = onChangeArray[1]
        self.enable_choose_source_id(display_mode)

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
        if mode_display == "CAPTURE CARD":
            self.manual_source_id.pack_forget()
            self.auto_source_id.pack(fill=tk.BOTH)
        else:
            self.auto_source_id.pack_forget()
            self.manual_source_id.pack(fill=tk.BOTH)

    def mode_changed(self, option):
        self.enable_choose_source_id(option)

        self.onChangeMode(self.mode_mapping[option])

    def manual_entry_changed(self, value):
        self.on_change_source_id(value)

    def capture_device_changed(self, option):
        self.on_change_source_id(str(option))

    def refresh(self, value):
        self.modeVar.set(value)
