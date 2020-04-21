from ocr_algo.DigitOCR import scoreImage
from ocr_algo.ScoreFixer import ScoreFixer
from ocr_algo.PieceStatsTextOCR import generate_stats
import ocr_algo.PieceStatsBoardOCR as PieceStatsBoardOCR
from ocr_state.piece_stats import PieceStatAccumulator
import ocr_algo.BoardOCR as BoardOCR
import ocr_algo.PreviewOCR2 as PreviewOCR
import ocr_algo.FlashOCR as FlashOCR
from ocr_algo.NewGameDetector import NewGameDetector

from calibrate import mainLoop as calibrateLoop
from config import config
from lib import (
    checkWindow,
    clamp,
    getWindow,
    mult_rect,
    runTasks,
    XYWHOffsetAndConvertToLTBR,
    WindowCapture,
)
from CachedSender import CachedSender
from multiprocessing import Pool
import multiprocessing
import threading
from Networking.NetworkClient import NetClient
from tkinter import messagebox
import time
import sys

# patterns for digits.
# A = 0->9 + A->F,
# D = 0->9
# B = 0->1 (das value only 00 to 16, so first digit can check 0 or 1 only) (B for Binary)
# T = 0->2 (majority of humans play up to level 29, so first digit of level could be 0-2 only) (T for Triplet)
PATTERNS = {
    "score": "ADDDDD" if config.get("performance.support_hex_score") else "DDDDDD",
    "lines": "DDD",
    "level": "AA" if config.get("performance.support_hex_level") else "TD",
    "stats": "DDD",
    "das": "BD",
}

STATS_METHOD = config.get("stats.capture_method")  # can be TEXT or FIELD.
CAPTURE_FIELD = config.get("calibration.capture_field")
CAPTURE_PREVIEW = config.get("calibration.capture_preview")
CAPTURE_FLASH = config.get("calibration.flash_method")
STATS_ENABLE = config.get("stats.enabled")
USE_STATS_FIELD = STATS_ENABLE and STATS_METHOD == "FIELD"
WINDOW_N_SLICE = config.get("performance.capture_method") == "WINDOW_N_SLICE"

# quick check for num_threads:
if WINDOW_N_SLICE and config.get("performance.num_threads") != 1:
    messagebox.showerror(
        "NESTrisOCR",
        "WINDOW_N_SLICE only supports one thread. Please change number of threads to 1",
    )
    sys.exit()


# The list of tasks to execute can be computed at bootstrap time
# to remove all conditional processing from the main running loop
def getWindowAreaAndPartialTasks():
    # gather list of all areas that need capturing
    # that will be used to determine the minimum window area to capture
    areas = {
        "score": mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.score")
        ),
        "lines": mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.lines")
        ),
        "level": mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.level")
        ),
    }

    if CAPTURE_FIELD:
        areas["field"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.field")
        )
        areas["color1"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.color1")
        )
        areas["color2"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.color2")
        )

    if USE_STATS_FIELD:
        areas["stats2"] = mult_rect(
            config.get("calibration.game_coords"), config.stats2_percentages
        )
    elif STATS_ENABLE:
        areas["stats"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.stats")
        )

    if CAPTURE_PREVIEW:
        areas["preview"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.preview")
        )

    if CAPTURE_FLASH == "BACKGROUND":
        areas["flash"] = mult_rect(
            config.get("calibration.game_coords"), config.get("calibration.pct.flash")
        )

    coords_list = areas.values()

    # compute the minimum window area to capture to cover all fields
    minWindowAreaTLRB = (
        min((coords[0] for coords in coords_list)),
        min((coords[1] for coords in coords_list)),
        max((coords[0] + coords[2] for coords in coords_list)),
        max((coords[1] + coords[3] for coords in coords_list)),
    )

    # convert minimum window coordinates to XYWH (needed by capture API)
    minWindowAreaXYWH = (
        minWindowAreaTLRB[0],
        minWindowAreaTLRB[1],
        minWindowAreaTLRB[2] - minWindowAreaTLRB[0],
        minWindowAreaTLRB[3] - minWindowAreaTLRB[1],
    )

    # Extract offset from minimal capture area
    offset = minWindowAreaXYWH[:2]

    partials = []

    def processCoordinates(coords):
        if WINDOW_N_SLICE:
            return XYWHOffsetAndConvertToLTBR(offset, coords)
        else:
            return coords

    methodPrefix = "extract" if WINDOW_N_SLICE else "capture"

    # prepare list of tasks to run at each loop
    for key, coords in areas.items():
        if key in ["score", "lines", "level"]:
            partials.append(
                (
                    eval(methodPrefix + "AndOCR"),
                    (processCoordinates(coords), PATTERNS[key], key, False,),
                )
            )

        elif key == "preview":
            partials.append(
                (eval(methodPrefix + "AndOCRPreview"), (processCoordinates(coords),))
            )

        elif key == "stats":
            stats_coords = generate_stats(
                config.get("calibration.game_coords"),
                config.get("calibration.pct.stats"),
                config.get("calibration.pct.score")[3],
            )

            for pieceKey, pieceCoords in stats_coords.items():
                partials.append(
                    (
                        eval(methodPrefix + "AndOCR"),
                        (
                            processCoordinates(pieceCoords),
                            PATTERNS[key],
                            pieceKey,
                            True,
                        ),
                    )
                )

        elif key == "stats2":
            # stats2 will only be read as a task in the main loop IF multithreading is disabled
            if MULTI_THREAD == 1:
                partials.append(
                    (
                        eval(methodPrefix + "AndOCRBoardPiece"),
                        (processCoordinates(coords),),
                    )
                )

        elif key == "field":
            partials.append(
                (
                    eval(methodPrefix + "AndOCRBoard"),
                    (
                        processCoordinates(coords),
                        processCoordinates(areas["color1"]),
                        processCoordinates(areas["color2"]),
                    ),
                )
            )
        elif key == "flash":
            partials.append(
                (
                    eval(methodPrefix + "AndOCRFlash"),
                    (
                        processCoordinates(coords),
                        config.get("calibration.flash_threshold"),
                    ),
                )
            )

    return minWindowAreaXYWH, partials


# piece stats and method. Recommend using FIELD
STATS2_COORDS = mult_rect(
    config.get("calibration.game_coords"), config.stats2_percentages
)

MULTI_THREAD = config.get(
    "performance.num_threads"
)  # shouldn't need more than four if using FieldStats + score/lines/level

# limit how fast we scan.
RATE_FIELDSTATS = 1 / 60.0 if WINDOW_N_SLICE else 1 / 120.0
RATE_TEXTONLY = 0.064
RATE_FIELD = 1.0 / clamp(15, 60, config.get("performance.scan_rate"))

if USE_STATS_FIELD and MULTI_THREAD == 1:
    RATE = RATE_FIELDSTATS
elif CAPTURE_FIELD or USE_STATS_FIELD or CAPTURE_FLASH == "BACKGROUND":
    RATE = RATE_FIELD
else:
    RATE = RATE_TEXTONLY

print("ScanRate:" + str(RATE))
# how are we calculating timestamp? Time.time, or from the file?
firstTime = time.time()


def getRealTimeStamp():
    return time.time() - firstTime


getTimeStamp = getRealTimeStamp
if config.get("calibration.capture_method") == "FILE":
    MULTI_THREAD = 1
    if config.get("network.protocol") == "FILE":
        RATE = 0.000
        getTimeStamp = WindowCapture.TimeStamp

SLEEP_TIME = 0.001


def captureAndOCR(hwnd, coords, digitPattern, taskName, red):
    img = WindowCapture.ImageCapture(coords, hwnd)
    return taskName, scoreImage(img, digitPattern, False, red)


def captureAndOCRBoardPiece(hwnd, coords):
    img = WindowCapture.ImageCapture(coords, hwnd)
    rgbo = PieceStatsBoardOCR.parseImage(img)
    return "piece_stats_board", rgbo


def captureAndOCRBoard(hwnd, boardCoords, color1Coords, color2Coords):
    img = WindowCapture.ImageCapture(boardCoords, hwnd)
    col1 = WindowCapture.ImageCapture(color1Coords, hwnd)
    col2 = WindowCapture.ImageCapture(color2Coords, hwnd)
    field = BoardOCR.parseImage(img, col1, col2)
    return "field", field


def captureAndOCRPreview(hwnd, previewCoords):
    img = WindowCapture.ImageCapture(previewCoords, hwnd)
    result = PreviewOCR.parseImage(img)
    return "preview", result


def captureAndOCRFlash(hwnd, flashCoords, limit):
    img = WindowCapture.ImageCapture(flashCoords, hwnd)
    result = FlashOCR.parseImage(img, limit)
    return "flash", result


def extractAndOCR(sourceImg, fieldCoords, digitPattern, taskName, red):
    img = sourceImg.crop(fieldCoords)
    return taskName, scoreImage(img, digitPattern, False, red)


def extractAndOCRBoardPiece(sourceImg, boardPieceCoords):
    img = sourceImg.crop(boardPieceCoords)
    rgbo = PieceStatsBoardOCR.parseImage(img)
    return "piece_stats_board", rgbo


def extractAndOCRBoard(sourceImg, boardCoords, color1Coords, color2Coords):
    img = sourceImg.crop(boardCoords)
    col1 = sourceImg.crop(color1Coords)
    col2 = sourceImg.crop(color2Coords)
    field = BoardOCR.parseImage(img, col1, col2)
    return "field", field


def extractAndOCRPreview(img, previewCoords):
    result = PreviewOCR.parseImage(img.crop(previewCoords))
    return "preview", result


def extractAndOCRFlash(img, flashCoords, limit):
    result = FlashOCR.parseImage(img.crop(flashCoords), limit)
    return "flash", result


# run this as fast as possible
def statsFieldMulti(ocr_stats, pool):
    while True:
        t = time.time()
        hwnd = getWindow()
        _, pieceType = pool.apply(captureAndOCRBoardPiece, (hwnd, STATS2_COORDS))
        ocr_stats.update(pieceType, t)
        if time.time() - t > 1 / 60.0:
            print("Warning, not scanning field fast enough", str(time.time() - t))

        # only sleep once.
        if time.time() < t + RATE_FIELDSTATS:
            time.sleep(SLEEP_TIME)


def main(onCap, checkNetworkClose):  # noqa: C901
    if MULTI_THREAD >= 2:
        p = Pool(MULTI_THREAD)
    else:
        p = None

    if USE_STATS_FIELD:
        accum = PieceStatAccumulator()
        lastLines = None  # use to reset accumulator
        if (
            MULTI_THREAD >= 2
        ):  # run Field_OCR as fast as possible; unlock from mainthread.
            thread = threading.Thread(target=statsFieldMulti, args=(accum, p))
            thread.daemon = True
            thread.start()

    scoreFixer = ScoreFixer(PATTERNS["score"])

    gameIDParser = NewGameDetector()
    finished = False
    while not finished:
        # outer loop waits for the window to exists
        frame_start = time.time()
        frame_end = frame_start + RATE
        hwnd = getWindow()

        if not hwnd:
            while time.time() < frame_end:
                time.sleep(SLEEP_TIME)
            continue

        windowMinCoords, partialTasks = getWindowAreaAndPartialTasks()

        while checkWindow(hwnd):
            # inner loop gets fresh data for just the desired window
            frame_start = time.time()
            frame_end = frame_start + RATE

            if WINDOW_N_SLICE:
                # capture min window area in one command first, will be sliced later
                source = WindowCapture.ImageCapture(windowMinCoords, hwnd)
            else:
                source = hwnd

            # inject source to complete partial tasks
            rawTasks = [(func, (source,) + args) for func, args in partialTasks]

            # run all tasks (in separate threads if MULTI_THREAD is enabled)
            result = runTasks(p, rawTasks)

            # update our accumulator
            if USE_STATS_FIELD:
                if lastLines is None and result["lines"] == "000":
                    accum.reset()

                if MULTI_THREAD == 1:
                    accum.update(result["piece_stats_board"], frame_start)
                    del result["piece_stats_board"]

                result.update(accum.toDict())
                lastLines = result["lines"]

                # warning for USE_STATS_FIELD if necessary
                if MULTI_THREAD == 1 and time.time() > frame_start + RATE_FIELD:
                    print("Warning, dropped frame scanning preview in field")

            if (
                config.get("calibration.capture_field")
                and time.time() > frame_start + RATE_FIELD
            ):
                print("Warning, dropped frame when capturing field")

            result["playername"] = config.get("player.name")
            result["gameid"], wasNewGameID = gameIDParser.getGameID(
                result["score"], result["lines"], result["level"]
            )

            if config.get("performance.support_hex_score"):
                if wasNewGameID:
                    scoreFixer.reset()
                # fix score's first digit. 8 to B and B to 8 depending on last state.
                result["score"] = scoreFixer.fix(result["score"])

            onCap(result, getTimeStamp())
            error = checkNetworkClose()
            if error is not None:
                return error
            while time.time() < frame_end - SLEEP_TIME:
                time.sleep(SLEEP_TIME)

            if not WindowCapture.NextFrame():  # finished reading video
                finished = True
                break


if __name__ == "__main__":
    multiprocessing.freeze_support()
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate":
        calibrateLoop()
        sys.exit()

    print("Creating net client...")
    client = NetClient.CreateClient(
        config.get("network.host"), int(config.get("network.port"))
    )
    print("Net client created.")
    cachedSender = CachedSender(
        client, config.get("debug.print_packet"), config.get("network.protocol")
    )

    result = None
    try:
        print("Starting main loop")
        result = main(cachedSender.sendResult, client.checkNetworkClose)
    except KeyboardInterrupt:
        pass
    print("main thread is here")
    print(result)

    if result is not None:
        # root = Tk()
        # root.withdraw()
        messagebox.showerror(
            "NESTrisOCR", "You have been kicked. Reason: " + str(result)
        )

    client.stop()
    client.join()
