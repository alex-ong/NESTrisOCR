import multiprocessing
from tkinter import messagebox
import time
import sys

from calibrate import mainLoop as calibrateLoop

from nestris_ocr.capturing import capture
from nestris_ocr.scan_strat.fastest_strategy import FastestStrategy as Strategy

# from scan_strat.naive_strategy import NaiveStrategy as Strategy
from nestris_ocr.network.network_client import NetClient

from nestris_ocr.network.cached_sender import CachedSender
from nestris_ocr.config import config
from nestris_ocr.utils.lib import WindowCapture

RATE = 1.0 / config["performance.scan_rate"]

# how are we calculating timestamp? Time.time, or from the file?
firstTime = time.time()


def getRealTimeStamp():
    return time.time() - firstTime


getTimeStamp = getRealTimeStamp
if config["calibration.capture_method"] == "FILE":
    if config["network.protocol"] == "FILE":
        RATE = 0.000
        getTimeStamp = WindowCapture.TimeStamp

SLEEP_TIME = 0.001


def main(on_cap, check_network_close):
    strategy = Strategy()

    # The outer loop makes sure that the program retries constantly even when
    # capturing device is having trouble
    while True:
        try:
            ts, image = capture.get_image(rgb=True)

            if not ts and not image:
                if config["debug.print_packet"]:
                    print("clean exit")

                break
        except Exception:
            time.sleep(RATE)
            continue

        frame_end_ts = ts + RATE

        strategy.update(ts, image)
        result = strategy.to_dict()

        if config["debug.print_packet"]:
            processing_time = time.time() - ts
            print(processing_time)
            print(result)

        # on_cap(result, getTimeStamp())

        # error = check_network_close()
        # if error is not None:
        #    return error

        time.sleep(max(frame_end_ts - time.time(), 0))


if __name__ == "__main__":
    multiprocessing.freeze_support()

    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate":
        calibrateLoop()
        sys.exit()

    print("Creating net client...")
    client = NetClient.CreateClient(config["network.host"], int(config["network.port"]))
    print("Net client created.")
    cachedSender = CachedSender(
        client, config["debug.print_packet"], config["network.protocol"]
    )

    result = None
    # try:
    print("Starting main loop")
    result = main(cachedSender.sendResult, client.checkNetworkClose)
    # except KeyboardInterrupt:
    #    pass
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
