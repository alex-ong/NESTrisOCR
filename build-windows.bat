rem We have committed the built numba plugins, so we shouldn't need to rebuild. Uncomment these lines to rebuild
rem You'll need MSVC 14.0 to build, as well as numba.

rem first, build the numba plugins
rem cd Networking
rem python buildByteStuffer2.py
rem cd ../OCRAlgo
rem python buildBoardOCR2.py

rem the following spec file assumes we don't need llvmlite since we've excluded numba.
pyinstaller -D main.spec



