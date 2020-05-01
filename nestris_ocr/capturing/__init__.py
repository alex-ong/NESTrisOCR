import time

from nestris_ocr.config import config

if config["calibration.capture_method"] == "OPENCV":
    from nestris_ocr.capturing.opencv import OpenCVCapture as Capture
else:
    raise ImportError("Invalid capture method")


capture = None


def init_capture(source_id, xywh_box):
    global capture

    capture = Capture(source_id, xywh_box)

    for i in range(5):
        try:
            _, image = capture.get_image()

            if image:
                print("Capture device ready!")
                break
        except Exception:
            print("Capture device not ready. {}...".format(i))
            time.sleep(1)
            continue
    else:
        print('Capture device cannot be found with "{}"'.format(source_id))


init_capture(config["calibration.source_id"], config["calibration.game_coords"])
