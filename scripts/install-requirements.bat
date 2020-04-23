REM simpleaudio currently needs to be compiled.
REM We've prebuilt a version here.
pip3 install wheel/simpleaudio-1.0.2-cp37-cp37m-win32.whl

REM here we install everything else
pip3 install -r ../requirements.txt
