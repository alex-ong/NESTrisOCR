from functools import partial
import tkinter as tk
import tkinter.ttk as ttk
import multiprocessing
import time
import sys

from PIL import Image
from nestris_ocr.calibration.bool_chooser import BoolChooser
from nestris_ocr.calibration.string_chooser import StringChooser
from nestris_ocr.calibration.rect_chooser import RectChooser, CompactRectChooser
from nestris_ocr.calibration.image_canvas import ImageCanvas
from nestris_ocr.calibration.draw_calibration import (
    draw_calibration,
    capture_das_trainer,
    capture_split_digits,
    capture_preview,
    capture_color1color2,
    capture_blackwhite,
    captureArea,
)
from nestris_ocr.calibration.other_options import create_window
from nestris_ocr.calibration.widgets import Button
from nestris_ocr.calibration.auto_calibrate import auto_calibrate_raw
from nestris_ocr.capturing import capture
from nestris_ocr.config import config
from nestris_ocr.ocr_algo.digit import finalImageSize, scoreImage0
from nestris_ocr.ocr_algo.preview2 import PreviewImageSize
from nestris_ocr.utils.lib import mult_rect

UPSCALE = 2
ENABLE_OTHER_OPTIONS = True

colorsImageSize = (80, 80)
blackWhiteImageSize = (80, 80)


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
            self.update_game_coords,
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
        self.tabManager.bind("<<NotebookTabChanged>>", self.redrawImages)

        self.setupTab1()
        self.setupTab2()
        self.setupTab3()
        self.setupTab4()
        self.setPreviewTextVisible()

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

        self.fieldCapture = tk.Frame(f)
        self.fieldCapture.grid(row=0, columnspan=2)

        self.fieldChooser = CompactRectChooser(
            self.fieldCapture,
            "field (imagePerc)",
            config["calibration.pct.field"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.field"),
        )
        self.fieldChooser.grid(row=0, columnspan=2)

        self.colorCapture = tk.Frame(self.fieldCapture)
        self.colorCapture.grid(row=1, columnspan=2)

        self.color1Chooser = CompactRectChooser(
            self.colorCapture,
            "Color1 (imagePerc)\nSelect whole block without black border",
            config["calibration.pct.color1"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.color1"),
        )
        self.color1Chooser.grid(row=0, column=0)
        self.color1Image = ImageCanvas(
            self.colorCapture, colorsImageSize[0], colorsImageSize[1]
        )
        self.color1Image.grid(row=0, column=1)

        self.color2Chooser = CompactRectChooser(
            self.colorCapture,
            "Color2 (imagePerc)\nSelect whole block without black border",
            config["calibration.pct.color2"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.color2"),
        )
        self.color2Chooser.grid(row=1, column=0)
        self.color2Image = ImageCanvas(
            self.colorCapture, colorsImageSize[0], colorsImageSize[1]
        )
        self.color2Image.grid(row=1, column=1)

        self.flashChooser = CompactRectChooser(
            f,
            "Flash (imagePerc)",
            config["calibration.pct.flash"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.flash"),
        )
        self.flashChooser.grid(row=1, columnspan=2)

        self.blackWhiteChooser = CompactRectChooser(
            f,
            "Black and White\nSelect an area with both pure white and pure black",
            config["calibration.pct.black_n_white"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.black_n_white"),
        )
        self.blackWhiteChooser.grid(row=2, column=0)
        self.blackWhiteImage = ImageCanvas(
            f, blackWhiteImageSize[0], blackWhiteImageSize[1]
        )
        self.blackWhiteImage.grid(row=2, column=1)

        self.pieceStatsChooser = CompactRectChooser(
            f,
            "pieceStats (imagePerc)",
            config["calibration.pct.stats"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.stats"),
        )
        self.pieceStatsChooser.grid(row=3, columnspan=2)

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

        self.tabManager.add(f, text="PreviewPiece")

    def setupTab4(self):
        f = tk.Frame(self.tabManager)

        self.dasEnabledChooser = BoolChooser(
            f,
            "Enable DAS Trainer specific capturing",
            config["calibration.capture_das"],
            self.gen_set_config_and_redraw("calibration.capture_das"),
        )
        self.dasEnabledChooser.grid(row=0, columnspan=2)

        # Current Piece

        self.dasCurrentPieceChooser = CompactRectChooser(
            f,
            "Current Piece (imagePerc)",
            config["calibration.pct.das.current_piece"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.das.current_piece"),
        )
        self.dasCurrentPieceChooser.grid(row=1, columnspan=2)

        canvasSize = [UPSCALE * 2 * i for i in PreviewImageSize]
        self.dasCurrentPieceImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.dasCurrentPieceImage.grid(row=2, columnspan=2)

        # Instant DAS

        canvasSize = [UPSCALE * i for i in finalImageSize(2)]
        Button(
            f,
            text="Auto Adjust Instant DAS \n Needs CURRENT DAS = 00",
            command=self.autoInstantDas,
            bg="red",
        ).grid(row=3, column=0)
        self.instantDasPercChooser = CompactRectChooser(
            f,
            "instantDas (imagePerc)",
            config["calibration.pct.das.instant_das"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.das.instant_das"),
        )
        self.instantDasPercChooser.grid(row=3, column=1)
        self.instantDasImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.instantDasImage.grid(row=4, columnspan=2)

        # Current piece DAS

        Button(
            f,
            text="Auto Adjust Current Piece DAS \n Needs START DAS = 00",
            command=self.autoCurrentPieceDas,
            bg="red",
        ).grid(row=5, column=0)
        self.currentPieceDasPercChooser = CompactRectChooser(
            f,
            "currentPieceDas (imagePerc)",
            config["calibration.pct.das.current_piece_das"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.das.current_piece_das"),
        )
        self.currentPieceDasPercChooser.grid(row=5, column=1)
        self.currentPieceDasImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.currentPieceDasImage.grid(row=6, columnspan=2)

        self.tabManager.add(f, text="DasTrainer")

    def setFlashVisible(self):
        show = False
        if self.config["calibration.flash_method"] == "BACKGROUND":
            show = True

        if show:
            self.flashChooser.grid()
        else:
            self.flashChooser.grid_forget()

    def setFieldTextVisible(self):
        if self.config["calibration.capture_field"] or (
            self.config["stats.enabled"]
            and self.config["stats.capture_method"] == "FIELD"
        ):
            self.fieldCapture.grid(row=0, columnspan=2)

            if self.config["calibration.dynamic_colors"]:
                self.colorCapture.grid()
            else:
                self.colorCapture.grid_forget()

        else:
            self.fieldCapture.grid_forget()

    def setStatsTextVisible(self):
        if (
            self.config["stats.enabled"]
            and self.config["stats.capture_method"] == "TEXT"
        ):
            self.pieceStatsChooser.grid()
        else:
            self.pieceStatsChooser.grid_forget()

    def setPreviewTextVisible(self):
        show = self.config["calibration.capture_preview"]
        if show:
            self.previewPiece.grid()
            self.previewImage.grid()
            self.dasCurrentPieceImage.grid()
            self.currentPieceDasImage.grid()
            self.instantDasImage.grid()
            self.samplePreviewImage.grid()
            self.samplePreviewLabel.grid()
        else:
            self.previewPiece.grid_forget()
            self.previewImage.grid_forget()
            self.dasCurrentPieceImage.grid_forget()
            self.currentPieceDasImage.grid_forget()
            self.instantDasImage.grid_forget()
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

    def update_game_coords(self, result):
        config["calibration.game_coords"] = result
        capture.xywh_box = result
        self.redrawImages()

    def redrawImages(self, event=None):
        self.lastUpdate = time.time()
        board = self.getNewBoardImage()
        if board is None:
            self.noBoard = True
            return
        else:
            self.noBoard = False

        self.boardImage.updateImage(board)

        if self.getActiveTab() == 0:  # text
            score_img, lines_img, level_img = capture_split_digits(self.config)
            score_img = score_img.resize((UPSCALE * i for i in finalImageSize(6)))
            lines_img = lines_img.resize((UPSCALE * i for i in finalImageSize(3)))
            level_img = level_img.resize((UPSCALE * i for i in finalImageSize(2)))
            self.linesImage.updateImage(lines_img)
            self.scoreImage.updateImage(score_img)
            self.levelImage.updateImage(level_img)

        elif self.getActiveTab() == 1:  # field
            color1Img, color2Img = capture_color1color2(self.config)
            color1Img = color1Img.resize(colorsImageSize)
            self.color1Image.updateImage(color1Img)

            color2Img = color2Img.resize(colorsImageSize)
            self.color2Image.updateImage(color2Img)

            blackWhiteImg = capture_blackwhite(self.config)
            blackWhiteImg = blackWhiteImg.resize(blackWhiteImageSize)
            self.blackWhiteImage.updateImage(blackWhiteImg)

        elif self.getActiveTab() == 2:  # preview
            preview_img = capture_preview(self.config)
            preview_img = preview_img.resize(
                (UPSCALE * 2 * i for i in PreviewImageSize)
            )
            self.previewImage.updateImage(preview_img)

        elif self.getActiveTab() == 3:  # DAS Trainer
            (
                current_piece_img,
                current_piece_das_img,
                instant_das_img,
            ) = capture_das_trainer(self.config)
            current_piece_img = current_piece_img.resize(
                (UPSCALE * 2 * i for i in current_piece_img.size)
            )
            instant_das_img = instant_das_img.resize(
                (UPSCALE * i for i in finalImageSize(2))
            )
            current_piece_das_img = current_piece_das_img.resize(
                (UPSCALE * i for i in finalImageSize(2))
            )

            self.instantDasImage.updateImage(instant_das_img)
            self.dasCurrentPieceImage.updateImage(current_piece_img)
            self.currentPieceDasImage.updateImage(current_piece_das_img)

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

    def autoCurrentPieceDas(self):
        bestRect = autoAdjustRectangle(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.das.current_piece_das"],
            2,
        )
        if bestRect is not None:
            self.levelPerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.das.current_piece_das"] = bestRect
        else:
            print("Please have current piece das on screen as 00")

    def autoInstantDas(self):
        bestRect = autoAdjustRectangle(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.das.instant_das"],
            2,
        )
        if bestRect is not None:
            self.levelPerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.das.instant_das"] = bestRect
        else:
            print("Please have instant das on screen as 00")

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


ASSET_ROOT = "nestris_ocr/assets/"


def LoadSamplePreview():
    im = Image.open(ASSET_ROOT + "sprite_templates/preview-reference.png")
    return im


def LoadSamplePreview2():
    im = Image.open(ASSET_ROOT + "sprite_templates/preview-reference-border.png")
    return im
