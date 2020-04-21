from functools import partial
import tkinter as tk
import tkinter.ttk as ttk
from .Widgets import Button
import sys
from PIL import Image
from lib import config, mult_rect
from ocr_algo.DigitOCR import finalImageSize, scoreImage0
from ocr_algo.PreviewOCR2 import PreviewImageSize
from calibration.StringChooser import StringChooser
from calibration.RectChooser import RectChooser, CompactRectChooser
from calibration.ImageCanvas import ImageCanvas
from calibration.draw_calibration import (
    draw_calibration,
    highlight_split_digits,
    highlight_preview,
    captureArea,
)
from calibration.OtherOptions import create_window
from calibration.auto_calibrate import auto_calibrate_raw
import multiprocessing

import time

UPSCALE = 2
ENABLE_OTHER_OPTIONS = True


class Calibrator(tk.Frame):
    def __init__(self, config):
        self.config = config
        root = tk.Tk()
        super().__init__(root)
        root.protocol("WM_DELETE_WINDOW", self.on_exit)
        root.focus_force()
        root.wm_title("NESTrisOCR calibrator")
        self.pack()
        self.root = root
        self.destroying = False
        root.config(background="black")
        StringChooser(
            self,
            "capture window starts with:",
            config["calibration.source_id"],
            self.gen_set_config_and_redraw("calibration.source_id"),
            20,
        ).grid(row=0, sticky="nsew")
        StringChooser(
            self,
            "player name",
            config["player.name"],
            partial(config.__setitem__, "player.name"),
            20,
        ).grid(row=1, sticky="nsew")
        if ENABLE_OTHER_OPTIONS:
            Button(
                self,
                text="Other options",
                command=lambda: create_window(
                    root, self.config, self.otherOptionsClosed
                ),
            ).grid(row=0, column=1)

        # window coords
        f = tk.Frame(self)
        r = RectChooser(
            f,
            "capture window coords (pixels)",
            config["calibration.game_coords"],
            False,
            self.gen_set_config_and_redraw("calibration.game_coords"),
        )
        r.config(relief=tk.FLAT, bd=5, background="orange")
        r.pack(side=tk.LEFT)
        self.winCoords = r
        # auto calibrate
        border = tk.Frame(f)
        border.config(relief=tk.FLAT, bd=5, background="orange")
        border.pack(side=tk.RIGHT, fill="both")
        autoCalibrate = Button(
            border,
            text="Automatically detect field",
            command=self.autoDetectField,
            bg="red",
        )
        autoCalibrate.pack(fill="both", expand=True)
        f.grid(row=2, column=0)

        # refresh
        Button(self, text="Refresh Image", command=self.redrawImages).grid(
            row=2, column=1, sticky="nsew"
        )

        border = tk.Frame(self)
        border.grid(row=3, column=0, sticky="nsew")
        border.config(relief=tk.FLAT, bd=5, background="orange")
        self.boardImage = ImageCanvas(border, 512, 224 * 2)
        self.boardImage.pack()

        self.tabManager = ttk.Notebook(self)
        self.tabManager.grid(row=3, column=1, sticky="nsew")

        self.setupTab1()
        self.setupTab2()
        self.setupTab3()

        self.redrawImages()
        self.lastUpdate = time.time()

    def setupTab1(self):
        f = tk.Frame(self.tabManager)
        canvasSize = [UPSCALE * i for i in finalImageSize(3)]
        Button(
            f,
            text="Auto Adjust Lines \nNeeds Lines = 000",
            command=self.autoLines,
            bg="red",
        ).grid(row=0, column=0)
        self.linesPerc = CompactRectChooser(
            f,
            "lines (imagePerc)",
            config["calibration.pct.lines"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.lines"),
        )
        self.linesPerc.grid(row=0, column=1)
        self.linesImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.linesImage.grid(row=1, columnspan=2)

        canvasSize = [UPSCALE * i for i in finalImageSize(6)]
        Button(
            f,
            text="Auto Adjust Score \n Needs Score = 000000",
            command=self.autoScore,
            bg="red",
        ).grid(row=2, column=0)
        self.scorePerc = CompactRectChooser(
            f,
            "score (imagePerc)",
            config["calibration.pct.score"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.score"),
        )
        self.scorePerc.grid(row=2, column=1)
        self.scoreImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.scoreImage.grid(row=3, columnspan=2)

        canvasSize = [UPSCALE * i for i in finalImageSize(2)]
        Button(
            f,
            text="Auto Adjust Level \n Needs Level = 00",
            command=self.autoLevel,
            bg="red",
        ).grid(row=4, column=0)
        self.levelPerc = CompactRectChooser(
            f,
            "level (imagePerc)",
            config["calibration.pct.level"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.level"),
        )
        self.levelPerc.grid(row=4, column=1)
        self.levelImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.levelImage.grid(row=5, columnspan=2)
        self.tabManager.add(f, text="NumberOCR")

    def setupTab2(self):
        f = tk.Frame(self.tabManager)
        a = CompactRectChooser(
            f,
            "field (imagePerc)",
            config["calibration.pct.field"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.field"),
        )
        b = CompactRectChooser(
            f,
            "Color1 (imagePerc)",
            config["calibration.pct.color1"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.color1"),
        )
        c = CompactRectChooser(
            f,
            "Color2 (imagePerc)",
            config["calibration.pct.color2"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.color2"),
        )
        d = CompactRectChooser(
            f,
            "Flash (imagePerc)",
            config["calibration.pct.flash"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.flash"),
        )

        self.flashPosition = d
        self.fieldCaptures = [a, b, c]
        self.pieceStats = CompactRectChooser(
            f,
            "pieceStats (imagePerc)",
            config["calibration.pct.stats"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.stats"),
        )
        a.grid()
        b.grid()
        c.grid()
        d.grid()

        self.pieceStats.grid()
        self.setFieldTextVisible()
        self.setStatsTextVisible()
        self.tabManager.add(f, text="FieldStats")

    def setupTab3(self):
        f = tk.Frame(self.tabManager)
        self.previewPiece = CompactRectChooser(
            f,
            "Next Piece (imagePerc)",
            config["calibration.pct.preview"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.preview"),
        )
        self.previewPiece.grid()

        canvasSize = [UPSCALE * 2 * i for i in PreviewImageSize]
        self.previewImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.previewImage.grid()

        self.samplePreviewImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        img = LoadSamplePreview()
        img = img.resize(canvasSize)
        self.samplePreviewImage.updateImage(img)
        self.samplePreviewImage.grid()
        self.samplePreviewLabel = tk.Label(
            f, text="Crop to a 2x4 block area with no black pixel borders"
        )
        self.samplePreviewLabel.grid()

        self.wsamplePreviewImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        img = LoadSamplePreview2()
        img = img.resize(canvasSize)
        self.wsamplePreviewImage.updateImage(img)
        self.wsamplePreviewImage.grid()
        self.wsamplePreviewLabel = tk.Label(
            f, text="Example of bad calibration (extra pixel borders)"
        )
        self.wsamplePreviewLabel.grid()
        self.setPreviewTextVisible()

        self.tabManager.add(f, text="PreviewPiece")

    def setFlashVisible(self):
        show = False
        if self.config["calibration.flash_method"] == "BACKGROUND":
            show = True

        if show:
            self.flashPosition.grid()
        else:
            self.flashPosition.grid_forget()

    def setFieldTextVisible(self):
        show = False
        if self.config["calibration.capture_field"] or (
            self.config["stats.enabled"]
            and self.config["stats.capture_method"] == "FIELD"
        ):
            show = True

        for item in self.fieldCaptures:
            if show:
                item.grid()
            else:
                item.grid_forget()

    def setStatsTextVisible(self):
        if (
            self.config["stats.enabled"]
            and self.config["stats.capture_method"] == "TEXT"
        ):
            self.pieceStats.grid()
        else:
            self.pieceStats.grid_forget()

    def setPreviewTextVisible(self):
        show = self.config["calibration.capture_preview"]
        if show:
            self.previewPiece.grid()
            self.previewImage.grid()
            self.samplePreviewImage.grid()
            self.samplePreviewLabel.grid()
        else:
            self.previewPiece.grid_forget()
            self.previewImage.grid_forget()
            self.samplePreviewImage.grid_forget()
            self.samplePreviewLabel.grid_forget()

    def getActiveTab(self):
        return self.tabManager.index(self.tabManager.select())

    def updateRedraw(self, func, result):
        func(result)
        self.redrawImages()

    def gen_set_config_and_redraw(self, key):
        def set_config_and_redraw(result):
            config[key] = result
            self.redrawImages()

        return set_config_and_redraw

    def redrawImages(self):
        self.lastUpdate = time.time()
        board = self.getNewBoardImage()
        if board is None:
            self.noBoard = True
            return
        else:
            self.noBoard = False

        self.boardImage.updateImage(board)

        if self.getActiveTab() == 0:  # text
            score_img, lines_img, level_img = highlight_split_digits(self.config)
            score_img = score_img.resize((UPSCALE * i for i in score_img.size))
            lines_img = lines_img.resize((UPSCALE * i for i in lines_img.size))
            level_img = level_img.resize((UPSCALE * i for i in level_img.size))
            self.linesImage.updateImage(lines_img)
            self.scoreImage.updateImage(score_img)
            self.levelImage.updateImage(level_img)
        if self.getActiveTab() == 2:  # preview
            preview_img = highlight_preview(self.config)
            preview_img = preview_img.resize(
                (UPSCALE * 2 * i for i in preview_img.size)
            )
            self.previewImage.updateImage(preview_img)

    def autoLines(self):
        bestRect = autoAdjustRectangle(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.lines"],
            3,
        )
        if bestRect is not None:
            self.linesPerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.lines"] = bestRect
        else:
            print("Please have score on screen as 000")

    def autoScore(self):
        bestRect = autoAdjustRectangle(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.score"],
            6,
        )
        if bestRect is not None:
            self.scorePerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.score"] = bestRect
        else:
            print("Please have score on screen as 000000")

    def autoLevel(self):
        bestRect = autoAdjustRectangle(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.level"],
            2,
        )
        if bestRect is not None:
            self.levelPerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.level"] = bestRect
        else:
            print("Please have score on screen as 00")

    def getNewBoardImage(self):
        return draw_calibration(self.config)

    def autoDetectField(self):
        rect = auto_calibrate_raw(self.config)
        if rect is not None:
            self.winCoords.show(rect)

    def update(self):
        if not self.destroying:
            if time.time() - self.lastUpdate > 5.0 and self.noBoard:
                self.redrawImages()
            super().update()

    def otherOptionsClosed(self):
        self.redrawImages()
        self.setStatsTextVisible()
        self.setFieldTextVisible()
        self.setFlashVisible()
        self.setPreviewTextVisible()

    def on_exit(self):
        self.destroying = True
        self.root.destroy()


# sources: PixelDimensions (w,h), RectPerc(x,y,w,h)
# out: RectPixel(x,y,x2,y2)
def pixelPercRect(dim, rectPerc):
    x1 = round(dim[0] * rectPerc[0])
    y1 = round(dim[1] * rectPerc[1])
    x2 = round(x1 + dim[0] * rectPerc[2])
    y2 = round(y1 + dim[1] * rectPerc[3])
    return x1, y1, x2, y2


def autoAdjustRectangle(capture_coords, rect, numDigits):
    # we can only run multi-thread on certain frameworks.
    if config["calibration.capture_method"] in ["OPENCV", "FILE"]:
        multi_thread = False
    else:
        multi_thread = True

    if multi_thread:
        p = multiprocessing.Pool()

    lowestScore = None
    # lowestOffset = None
    bestRect = None
    pattern = "D" * numDigits
    left, right = -3, 4
    results = []
    total = (right - left) ** 4
    i = 0
    for x in range(left, right):
        for y in range(left, right):
            for w in range(left, right):
                for h in range(left, right):
                    newRect = (
                        rect[0] + x * 0.001,
                        rect[1] + y * 0.001,
                        rect[2] + w * 0.001,
                        rect[3] + h * 0.001,
                    )
                    pixRect = mult_rect(capture_coords, newRect)
                    if multi_thread:
                        results.append(
                            p.apply_async(adjustTask, (pixRect, pattern, newRect))
                        )
                    else:  # run directly.
                        results.append(adjustTask(pixRect, pattern, newRect))
                        progressBar(i, total)
                    i += 1

    for (i, r) in enumerate(results):
        if multi_thread:
            result, newRect = r.get()
        else:
            result, newRect = r
        progressBar(i, total)
        if result is not None:
            if lowestScore is None or result < lowestScore:
                bestRect = newRect
                lowestScore = result

    if multi_thread:
        p.close()
        p.join()

    return bestRect


def adjustTask(pixRect, pattern, newRect):
    result = 0
    for i in range(3):
        img = captureArea(pixRect)
        result2 = scoreImage0(img, pattern)
        if result2 is not None and result is not None:
            result += result2
        else:
            result = None
    return result, newRect


def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = "-" * int(round(percent * bar_length) - 1) + ">"
    spaces = " " * (bar_length - len(arrow))

    sys.stdout.write(
        "\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100)))
    )
    sys.stdout.flush()


def LoadSamplePreview():
    im = Image.open("assets/sprite_templates/preview-reference.png")
    return im


def LoadSamplePreview2():
    im = Image.open("assets/sprite_templates/preview-reference-border.png")
    return im
