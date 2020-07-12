from functools import partial
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk


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
)


from nestris_ocr.calibration.auto_calibrate import auto_calibrate_raw
from nestris_ocr.calibration.auto_number import auto_adjust_numrect
from nestris_ocr.calibration.capture_method import CaptureMethod
from nestris_ocr.calibration.other_options import create_window
from nestris_ocr.calibration.state_vis import StateVisualizer
from nestris_ocr.calibration.widgets import Button
from nestris_ocr.capturing import uncached_capture, reinit_capture
from nestris_ocr.config import config
from nestris_ocr.ocr_algo.dasTrainerCurPiece import CurPieceImageSize
from nestris_ocr.ocr_algo.digit import finalImageSize
from nestris_ocr.ocr_algo.preview2 import PreviewImageSize
from nestris_ocr.scan_strat.scan_helpers import refresh_window_areas
from nestris_ocr.scan_strat.naive_strategy import NaiveStrategy as Strategy
import nestris_ocr.utils.time as time

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
        self.strategy = Strategy()
        self.exit_program = True
        self.exit_calibrator = False
        CaptureMethod(
            self,
            (config["capture.method"], config["capture.source_id"]),
            (
                self.gen_set_reload_capture("capture.method"),
                self.gen_set_reload_capture("capture.source_id"),
                partial(config.__setitem__, "capture.source_id"),
            ),
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
        Button(self, text="Switch to SIMPLE Mode", command=self.simple_mode).grid(
            row=1, column=1
        )
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
        Button(self, text="Refresh Image", command=self.redrawImages, bg="blue").grid(
            row=2, column=1, sticky="nsew", rowspan=2,
        )

        # webcam output
        self.setupPlaybackTabs()
        self.playbackTabs.grid(row=4, column=0, sticky="nsew")
        self.calibrationTabs = ttk.Notebook(self)
        self.calibrationTabs.grid(row=4, column=1, sticky="nsew")
        self.calibrationTabs.bind("<<NotebookTabChanged>>", self.redrawImages)

        self.setupTab1()
        self.setupTab2()
        self.setupTab3()
        self.setupTab4()
        self.setupTab5()
        self.setPreviewTextVisible()

        self.progress_bar = ttk.Progressbar(
            self, orient=tk.HORIZONTAL, length=512, mode="determinate"
        )
        self.progress_bar["maximum"] = 100
        self.progress_bar.grid(row=5, columnspan=2, sticky="nsew")

        self.redrawImages()
        self.lastUpdate = time.time()
        reinit_capture()

    def simple_mode(self):
        config["calibrator.ui"] = "SIMPLE"
        self.exit_program = False
        self.exit_calibrator = True

    def setupPlaybackTabs(self):
        self.playbackTabs = ttk.Notebook(self)

        # capture device output
        f = tk.Frame(self.playbackTabs)
        border = tk.Frame(f)
        border.grid(row=4, column=0, sticky="nsew")
        border.config(relief=tk.FLAT, bd=5, background="orange")
        self.boardImage = ImageCanvas(border, 512, 224 * 2)
        self.boardImage.pack()

        self.playbackTabs.add(f, text="Capture Device")

        # game output
        f = tk.Frame(self.playbackTabs)
        self.boardImage2 = ImageCanvas(f, 240, 224)
        self.boardImage2.grid(row=0, column=0, sticky="E")
        self.stateVisualizer = StateVisualizer(f)
        self.stateVisualizer.grid(row=0, column=1, sticky="W")
        self.playbackTabs.add(f, text="OCR Output")

    def setupTab1(self):
        f = tk.Frame(self.calibrationTabs)
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
        self.linesPerc.grid(row=0, column=1, rowspan=2)
        self.linesImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.linesImage.grid(row=1, column=0)

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
        self.scorePerc.grid(row=2, column=1, rowspan=2)
        self.scoreImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.scoreImage.grid(row=3, column=0)

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
        self.levelPerc.grid(row=4, column=1, rowspan=2)
        self.levelImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.levelImage.grid(row=5, column=0)
        self.calibrationTabs.add(f, text="NumberOCR")

    def setupTab2(self):
        f = tk.Frame(self.calibrationTabs)

        self.fieldCapture = tk.Frame(f)
        self.fieldCapture.grid(row=0, columnspan=2)

        self.fieldChooser = CompactRectChooser(
            self.fieldCapture,
            "field (imagePerc)",
            config["calibration.pct.field"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.field"),
        )
        self.fieldChooser.grid(row=0)

        self.colorCapture = tk.Frame(self.fieldCapture)
        self.colorCapture.grid(row=1)

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

        self.calibrationTabs.add(f, text="FieldStats")

    def setupTab3(self):
        f = tk.Frame(self.calibrationTabs)
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

        self.calibrationTabs.add(f, text="PreviewPiece")

    def setupTab4(self):
        f = tk.Frame(self.calibrationTabs)
        self.flashChooser = CompactRectChooser(
            f,
            "Flash (imagePerc)",
            config["calibration.pct.flash"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.flash"),
        )
        self.flashChooser.grid(row=1, columnspan=2)

        self.blackWhiteCapture = tk.Frame(f)
        self.blackWhiteCapture.grid(row=2, columnspan=2)

        self.blackWhiteChooser = CompactRectChooser(
            self.blackWhiteCapture,
            "Black and White\nSelect an area with both pure white and pure black",
            config["calibration.pct.black_n_white"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.black_n_white"),
        )
        self.blackWhiteChooser.grid(row=0, column=0)
        self.blackWhiteImage = ImageCanvas(
            self.blackWhiteCapture, blackWhiteImageSize[0], blackWhiteImageSize[1]
        )
        self.blackWhiteImage.grid(row=0, column=1)

        self.pieceStatsChooser = CompactRectChooser(
            f,
            "pieceStats (imagePerc)",
            config["calibration.pct.stats"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.stats"),
        )
        self.pieceStatsChooser.grid(row=3, columnspan=2)

        self.setDynamicBWVisible()
        self.setStatsTextVisible()
        self.calibrationTabs.add(f, text="Misc.")

    def setupTab5(self):
        f = tk.Frame(self.calibrationTabs)

        self.dasEnabledChooser = BoolChooser(
            f,
            "Enable DAS Trainer specific capturing",
            config["calibration.capture_das"],
            self.gen_set_config_and_redraw("calibration.capture_das"),
        )
        self.dasEnabledChooser.grid(row=0, columnspan=2)

        # Current Piece
        canvasSize = [UPSCALE * 2 * i for i in CurPieceImageSize]
        self.dasCurrentPieceImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.dasCurrentPieceImage.grid(row=1, column=0)

        self.dasCurrentPieceChooser = CompactRectChooser(
            f,
            "Current Piece (imagePerc)",
            config["calibration.pct.das.current_piece"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.das.current_piece"),
        )
        self.dasCurrentPieceChooser.grid(row=1, column=1)

        # Instant DAS
        canvasSize = [UPSCALE * i for i in finalImageSize(2)]

        Button(
            f,
            text="Auto Adjust Instant DAS \n Needs CURRENT DAS = 00",
            command=self.autoInstantDas,
            bg="red",
        ).grid(row=2, column=0)
        self.instantDasPercChooser = CompactRectChooser(
            f,
            "instantDas (imagePerc)",
            config["calibration.pct.das.instant_das"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.das.instant_das"),
        )
        self.instantDasPercChooser.grid(row=2, column=1, rowspan=2)
        self.instantDasImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.instantDasImage.grid(row=3, column=0)

        # Current piece DAS
        Button(
            f,
            text="Auto Adjust Current Piece DAS \n Needs START DAS = 00",
            command=self.autoCurrentPieceDas,
            bg="red",
        ).grid(row=4, column=0)

        self.currentPieceDasPercChooser = CompactRectChooser(
            f,
            "currentPieceDas (imagePerc)",
            config["calibration.pct.das.current_piece_das"],
            True,
            self.gen_set_config_and_redraw("calibration.pct.das.current_piece_das"),
        )
        self.currentPieceDasPercChooser.grid(row=4, column=1, rowspan=2)
        self.currentPieceDasImage = ImageCanvas(f, canvasSize[0], canvasSize[1])
        self.currentPieceDasImage.grid(row=5, column=0)

        self.calibrationTabs.add(f, text="DasTrainer")

    def setFlashVisible(self):
        show = False
        if self.config["calibration.flash_method"] == "BACKGROUND":
            show = True

        if show:
            self.flashChooser.grid()
        else:
            self.flashChooser.grid_forget()

    def setDynamicBWVisible(self):
        if self.config["calibration.dynamic_black_n_white"]:
            self.blackWhiteCapture.grid(row=2, columnspan=2)
        else:
            self.blackWhiteCapture.grid_forget()

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
            self.samplePreviewImage.grid()
            self.samplePreviewLabel.grid()
        else:
            self.previewPiece.grid_forget()
            self.previewImage.grid_forget()
            self.samplePreviewImage.grid_forget()
            self.samplePreviewLabel.grid_forget()

    def getCalibrationTab(self):
        return self.calibrationTabs.index(self.calibrationTabs.select())

    def getPlaybackTab(self):
        return self.playbackTabs.index(self.playbackTabs.select())

    def updateRedraw(self, func, result):
        func(result)
        refresh_window_areas()
        self.redrawImages()

    def gen_set_reload_capture(self, key):
        def sub_function(result):
            config[key] = result
            reinit_capture()
            self.strategy = Strategy()
            refresh_window_areas()
            self.redrawImages()

        return sub_function

    def gen_set_config_and_redraw(self, key):
        def set_config_and_redraw(result):
            config[key] = result
            refresh_window_areas()
            self.redrawImages()

        return set_config_and_redraw

    def update_game_coords(self, result):
        config["calibration.game_coords"] = result
        uncached_capture().xywh_box = result
        refresh_window_areas()
        self.redrawImages()

    def updateActiveCalibrationTab(self):
        activeTab = self.getCalibrationTab()
        if activeTab == 0:  # text
            score_img, lines_img, level_img = capture_split_digits(self.config)
            score_img = score_img.resize((UPSCALE * i for i in finalImageSize(6)))
            lines_img = lines_img.resize((UPSCALE * i for i in finalImageSize(3)))
            level_img = level_img.resize((UPSCALE * i for i in finalImageSize(2)))
            self.linesImage.updateImage(lines_img)
            self.scoreImage.updateImage(score_img)
            self.levelImage.updateImage(level_img)

        elif activeTab == 1:  # field
            color1Img, color2Img = capture_color1color2(self.config)
            color1Img = color1Img.resize(colorsImageSize)
            self.color1Image.updateImage(color1Img)

            color2Img = color2Img.resize(colorsImageSize)
            self.color2Image.updateImage(color2Img)

            blackWhiteImg = capture_blackwhite(self.config)
            blackWhiteImg = blackWhiteImg.resize(blackWhiteImageSize)
            self.blackWhiteImage.updateImage(blackWhiteImg)

        elif activeTab == 2:  # preview
            preview_img = capture_preview(self.config)
            preview_img = preview_img.resize(
                (UPSCALE * 2 * i for i in PreviewImageSize)
            )
            self.previewImage.updateImage(preview_img)
        elif activeTab == 3:  # misc
            pass  # no images
        elif activeTab == 4:  # DAS Trainer
            (
                current_piece_img,
                current_piece_das_img,
                instant_das_img,
            ) = capture_das_trainer(self.config)
            current_piece_img = current_piece_img.resize(
                (UPSCALE * 2 * i for i in CurPieceImageSize)
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

    def updateActivePlaybackTab(self):
        activeTab = self.getPlaybackTab()
        if activeTab == 0:
            board = self.getNewBoardImage()
            self.boardImage.updateImage(board)
        elif activeTab == 1:
            ts, image = uncached_capture().get_image(rgb=True)
            self.boardImage2.updateImage(image.resize((240, 224)))
            self.strategy.update(ts, image)
            data = self.strategy.to_dict()
            self.stateVisualizer.updateValues(data)

    def redrawImages(self, event=None):
        self.lastUpdate = time.time()
        refresh_window_areas()
        self.updateActiveCalibrationTab()
        self.updateActivePlaybackTab()

    def autoNumber(self, name, num_digits):
        bestRect = auto_adjust_numrect(
            self.config["calibration.game_coords"],
            self.config["calibration.pct." + name],
            num_digits,
            self.update_progressbar,
        )
        if bestRect is not None:
            self.config["calibration.pct." + name] = bestRect
            refresh_window_areas()
            self.redrawImages()
        else:
            self.show_error(
                f"Failed to calibrate {name}\nTry again; or use advanced mode"
            )
        return bestRect

    def show_error(self, msg):
        messagebox.showerror("Error", msg)

    def autoLines(self):
        return self.autoNumber("lines", 3)

    def autoScore(self):
        return self.autoNumber("score", 6)

    def autoLevel(self):
        return self.autoNumber("level", 2)

    def autoCurrentPieceDas(self):
        return self.autoNumber("das.current_piece_das", 2)

    def autoInstantDas(self):
        return self.autoNumber("das.instant_das", 2)

    def getNewBoardImage(self):
        return draw_calibration(self.config)

    def autoDetectField(self):
        rect = auto_calibrate_raw(self.config)
        if rect is not None:
            self.winCoords.show(rect)

    def update_progressbar(self, perc):
        self.progress_bar["value"] = round(perc * 100)
        self.progress_bar.update()

    def update(self):
        if not self.destroying:
            if time.time() - self.lastUpdate > 1.0:
                self.redrawImages()
            super().update()

    def otherOptionsClosed(self):
        self.redrawImages()
        self.setStatsTextVisible()
        self.setDynamicBWVisible()
        self.setFlashVisible()
        self.setPreviewTextVisible()

    def on_exit(self):
        self.destroying = True
        self.exit_calibrator = True
        if self.root is not None:
            self.root.destroy()
            self.root = None


# sources: PixelDimensions (w,h), RectPerc(x,y,w,h)
# out: RectPixel(x,y,x2,y2)
def pixelPercRect(dim, rectPerc):
    x1 = round(dim[0] * rectPerc[0])
    y1 = round(dim[1] * rectPerc[1])
    x2 = round(x1 + dim[0] * rectPerc[2])
    y2 = round(y1 + dim[1] * rectPerc[3])
    return x1, y1, x2, y2


ASSET_ROOT = "nestris_ocr/assets/"


def LoadSamplePreview():
    im = Image.open(ASSET_ROOT + "sprite_templates/preview-reference.png")
    return im


def LoadSamplePreview2():
    im = Image.open(ASSET_ROOT + "sprite_templates/preview-reference-border.png")
    return im
