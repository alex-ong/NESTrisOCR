import time
from fastocr import scoreImage
import cv2
import mss
import numpy
from PIL import Image


with mss.mss() as sct:
    # Part of the screen to capture
    monitor_number = 1
    mon = sct.monitors[monitor_number]
    
    monitor = {"top": mon["top"] + 342, 
                "left": mon["left"]+1775, 
                "width": 181, 
                "height": 27, 
                "mon": monitor_number
              }

    while "Screen capturing":
        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        print (scoreImage(img))
        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
        