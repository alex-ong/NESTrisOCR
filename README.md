NESTrisOCR
===
Simple OCR, captures subset of OBS window, then processes relevant numbers.
Forwards results via TCP.

Look at `OCRAlgo/DigitOCR.py` to see image processing of numbers, and `OCRAlgo/PieceStatsBoardOCR.py` for processing of board to piece.
Algorithm is simple KNearest (compare image to reference images, sum of difference of pixels)


Requirements
===

Windows
=====
You need a working python installation to get everything running.

`python37-32` [Download here](https://www.python.org/downloads/release/python-372/)

When installing, make sure you `add to path` - this lets you run python from command prompt from any folder.

Double click `install-requirements.bat`. This will install all the other libraries required.

You can verify they are installed by running python from the command prompt and then importing the modules

`python`

`import PIL` 

`import win32ui`

`import numpy`

`import ConfigUpdater`

`import cv2`


You shouldnt get any errors. Then, exit python
`exit()`


OSX
=====

You need to have python3 and the pyobjc binding to access the Quartz APIs

At the command line, run:

`brew install python3 libtiff libjpeg webp little-cms2 opencv@2`

`pip3 install -r requirements-osx.txt`

You can verify the installation is correct by checking this:

`import PIL`

`import Quartz`

`import numpy`

`import numba`

`import ConfigUpdater`

`import cv2`


You shouldnt get any errors. Then, exit python
`exit()`


Calibration
===

Setup the target window:

1) First, open the application that has your window capture. This will be OBS or an emulator.

2) Note down it's game window name. Go into the game view (the one with the field).

3) Position and scale your application window to where you want it. **Since we capture the screen, any time you scale or move your application window, the calibration will be invalid**. 

4) You can use Windows+arrow keys to position the window so it will lock to the side or quarter of the screen.

Double-click on `calibrate.py`.

![calibration](https://github.com/alex-ong/NESTrisOCR/blob/master/assets/doc/example-calibration.png)

Follow the steps in the picture:

1) Enter the first few characters of the window name. Your window should show up in the preview pane.

2) Enter your name 

3) Press auto-calibrate. The window should snap into place. Check that hte game window has been detected. If not, press auto-calibrate another 3-4 times. If that still doesnt work,
   use the +- buttons in "capture window coords" to get the game window.

4) Auto adjust Lines, Score and Level. Micro adjust so that the numbers are close and then re-auto-adjust to get best results.

5) You can adjust other options such as multi-threading for performance and whether to capture piece stats or the field.

6) If capturing the field (whether for piece stats or field directly), calibrate the field in the field tab. There are also
   two squares that refer to the statistics portion of the screen so that we can ascertain block colors.

7) If capturing the piece statistics via text, calibrate so that the red text is highlighted correctly.

Running
===
Double-click `main.py` if you have installed python correctly.

If you are not familiar with command prompt, [google it...](https://www.google.com/search?q=how+to+change+directory+in+command+prompt)

You'll want to open a command prompt, change to the directory of this repository, then run this python file.


Testing
===
The window should print out your current state.

`{'lines': '000', 'score', '000120', 'level', '00'}`

If you have are capturing piece stats:

`{'score': '642572', 'lines': '147', 'level': '20', 'T': '004', 'J': '010', 'Z': '011', 'O': '005', 'S': '010', 'L': '008', 'I': '009'}`

If you are in a menu, it will more likely output

`{'lines': None, 'score', None, 'level', None}`

It will output via TCP to port 3338 by default. This is to connect to other applications that actually use the data.
