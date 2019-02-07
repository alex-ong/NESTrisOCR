NESTrisOCR
===
Simple OCR, captures subset of OBS window, then processes relevant numbers.
Forwards results via TCP.

Look at fastocr.py to see image processing, in particular brightness adjustment for red numbers.
Algorithm is simple KNearest (compare image to reference images, sum of difference of pixels)



Requirements
===
pillow
pypiwin32

Running
===
`python screencap.py`

Calibration
===
All calibration is in calibration.py and screencap.py

screencap.py

Use the following to calibrate:
CALIBRATION - turns calibration on. Program runs the following test images then exits.

* CALIBRATE_WINDOW - shows what you are capturing, overlaying the score,lines,level and stats

* CALIBRATE_SCORE 

* CALIBRATE_LINES 

* CALIBRATE_LEVEL 

* CALIBRATE_STATS 

calibration.py

* WINDOW_NAME - the obs window name. it must start with these characters.

* CAPTURE_COORDS - pixel offset of window to capture. Start with (0,0, 200,200) and go from there...

* _____Perc - shouldn't need to adjust, but can slightly adjust to get pixel perfect, which will increase accuracy.

Testing
===
Uncomment `#print message`, and see what is being outputted.
