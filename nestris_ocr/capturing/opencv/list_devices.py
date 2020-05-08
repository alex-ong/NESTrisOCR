import platform
import cv2

# two methods to list webcams:
# https://stackoverflow.com/questions/8044539/listing-available-devices-in-python-opencv
# and
# https://www.codeproject.com/Articles/5163142/List-Capture-Devices-for-Python-OpenCV-on-Windows

try:
    import nestris_ocr.capturing.opencv.device as device
except ImportError:
    device = None


def get_device_list():
    device_list = None

    if platform.system() == "Windows" and device is not None:
        # Get camera list
        try:
            device_list = device.getDeviceList()
            device_list = list(enumerate(device_list))
            return device_list
        except:  # noqa  E722
            pass

    if device_list is None:
        index = 0
        device_list = []
        for i in range(8):  # maximum 8 webcam support
            cap = cv2.VideoCapture(i)
            if not cap.read()[0]:
                break
            else:
                device_list.append((index, "Device " + str(i)))
            cap.release()
            index += 1
        return device_list
