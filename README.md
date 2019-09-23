NESTrisOCR
===
Simple OCR, captures subset of OBS window, then processes relevant numbers.
Forwards results via TCP.

Look at `fastocr.py` to see image processing of numbers, and `boardocr.py` for processing of board to piece.
Algorithm is simple KNearest (compare image to reference images, sum of difference of pixels)


Requirements
===

Windows
=====
You need a working python installation to get everything running.

`python37-32` [Download here](https://www.python.org/downloads/release/python-372/)

When installing, make sure you `add to path` - this lets you run python from command prompt from any folder.

Next, [open a command window](https://www.google.com/search?q=how+to+open+a+command+prompt+windows). type in the following commands to install some modules required for this program

`pip install pillow`

`pip install pypiwin32`

`pip install numpy`

You can verify they are installed by running python from the command prompt and then importing the modules
`python`

`import PIL` 

`import win32ui`

`import numpy`


You shouldnt get any errors. Then, exit python
`exit()`


OSX
=====

You need to have python3 and the pyobjc binding to access the Quartz APIs

At the command line, run:

`brew install python3 libtiff libjpeg webp little-cms2`

`pip3 install -U pyobjc pillow numpy`

You can verify the installation is correct by checking this:

`import PIL`

`import Quartz`

`import numpy`


You shouldnt get any errors. Then, exit python
`exit()`


Running
===
`python main.py`

Alternatively you can double-click main.py if you are on windows and have installed python correctly.

If you are not familiar with command prompt, [google it...](https://www.google.com/search?q=how+to+change+directory+in+command+prompt)

You'll want to open a command prompt, change to the directory of this repository, then run this python file.


Calibration
===
![calibration](https://github.com/alex-ong/NESTrisOCR/blob/master/assets/doc/example-calibration.png)

All calibration is in `calibrate.py` and `config.ini`

You need to set simply run `calibrate.py` and see what image it spits out.

It will spit out an image. Run the program repeatedly, tweaking the `config.ini` until it looks right


**config.ini**

* `WINDOW_NAME` - the obs window name. it must start with these characters.

* `CAPTURE_COORDS` - pixel offset of window to capture. Start with (0,0, 200,200) and go from there...

* `_____Perc` - shouldn't need to adjust, but can slightly adjust to get pixel perfect, which will increase accuracy.


Testing
===
The window should print out your current state.

`{'lines': '000', 'score', '000120', 'level', '00'}`

If you have STATS_ENABLE:

`{'score': '642572', 'lines': '147', 'level': '20', 'T': '004', 'J': '010', 'Z': '011', 'O': '005', 'S': '010', 'L': '008', 'I': '009'}`

If you are in a menu, it will more likely output

`{'lines': None, 'score', None, 'level', None}`

It will output via TCP to port 3338 by default. THis is to connect to other applications that actually use the data.
