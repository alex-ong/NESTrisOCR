Pip install these specific versions:

setuptools==44.0.0
pyinstaller==3.6


Numpy
===
Install numpy vanilla; this removes OpenBLAS at the expense of speed:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

`pip install some-package.whl`

Alternatively, you can try excluding the `OpenBLAS` dll, since numpy probably 
only crashes if you use linear algebra, so it should still work(?) 
TODO: test this

OpenCV
===
Use:
`pip install opencv-python-headless`

since we don't need Qt4/5 to display anything