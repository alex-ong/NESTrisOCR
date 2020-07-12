import platform


from nestris_ocr.config import config
from nestris_ocr.capturing.null import NullCapture
import nestris_ocr.utils.time as time


def get_capture_class():
    capture_method = config["capture.method"]

    if capture_method == "STATIC":
        from nestris_ocr.capturing.static import StaticCapture

        return StaticCapture
    elif capture_method == "OPENCV":
        from nestris_ocr.capturing.opencv import OpenCVCapture

        return OpenCVCapture
    elif capture_method == "FILE":
        from nestris_ocr.capturing.file import FileCapture

        return FileCapture
    elif capture_method == "WINDOW" and platform.system() == "Windows":
        from nestris_ocr.capturing.win32 import Win32Capture

        return Win32Capture
    elif capture_method == "WINDOW" and platform.system() == "Darwin":
        mac_ver = platform.mac_ver()[0]
        major, minor, patch = mac_ver.split(".")

        if int(major) * 100 + int(minor) > 1014:
            raise ImportError(
                "Unsupported Mac OS version. "
                "Window capture is supported up to Mojave (10.14)"
            )

        from nestris_ocr.capturing.quartz import QuartzCapture

        return QuartzCapture
    elif capture_method == "WINDOW" and platform.system() == "Linux":
        from nestris_ocr.capturing.linux import LinuxCapture

        return LinuxCapture
    else:
        raise ImportError("Invalid capture method: " + capture_method)


capture = None


def init_capture(source_id, xywh_box, extra_data, fast):
    global capture

    try:
        capture_class = get_capture_class()
    except ImportError as e:
        print(e)
        capture_class = NullCapture

    if fast and isinstance(capture, capture_class):
        capture.fast_reinit(source_id, xywh_box, extra_data)
    else:
        capture = capture_class(source_id, xywh_box, extra_data)

    for i in range(50):
        try:
            _, image = capture.get_image()

            if image:
                print("Capture device ready!")
                config["capture.source_extra_data"] = capture.extra_data
                break

        except Exception:
            print(f"Capture device not ready. {i}")
            time.sleep(0.1)
            continue
    else:
        print(f'Capture device cannot be found with "{source_id}"')
        capture = NullCapture(source_id, xywh_box, extra_data)


# only opencv needs true re-initting.
def reinit_capture():
    global capture
    fast_init = False
    if capture is not None:
        capture.stop()
        fast_init = capture.fast_restart()

    init_capture(
        config["capture.source_id"],
        config["calibration.game_coords"],
        config["capture.source_extra_data"],
        fast_init,
    )


# Get the latest reference to capture
def uncached_capture():
    global capture
    return capture


reinit_capture()
