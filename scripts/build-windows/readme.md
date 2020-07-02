Quick start
===
Create a `virtualenvironment`, then just run `build-windows-sysdate.bat`
It will create a zip folder.



Main changes for modules are below:

PyInstaller
===

setuptools==44.0.0
pyinstaller==3.6


Numpy
===
Install numpy vanilla; this removes OpenBLAS at the expense of speed:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

`pip install some-package.whl`


You can't just install `pip install numpy` and then exclude the OpenBLAS dll.

OpenCV
===
Use:
`pip install opencv-python-headless`

since we don't need Qt4/5 to display anything

Building
===

Ideally we use build.yml and pass in tag name to get a build.
For testing locally, you can use `build-windows-sysdate.bat`