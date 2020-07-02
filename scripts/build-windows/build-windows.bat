echo Building to %1.zip

rem We have committed the built numba plugins, so we shouldn't need to rebuild. Uncomment these lines to rebuild
rem You'll need MSVC 14.0 to build, as well as numba.
pip install -r requirements.txt

rem first, build the numba plugins
cd ..\..\nestris_ocr\network
python build_native_field_packer.py
cd ..\ocr_algo
python build_fastboard.py

rem come back to where we started
cd ..\..\scripts\build-windows

rem the following spec file assumes we don't need llvmlite since we've excluded numba.
copy main.spec ..\..\main.spec
cd ..\..
pyinstaller -D main.spec

rem copy the scripts to run the program
copy scripts\build-windows\dist\calibrate.bat dist\
copy scripts\build-windows\dist\main.bat dist\

rem zip everything neatly.
zip-folder dist -f NESTrisOCR-%1 -o NESTrisOCR-%1.zip

rem Come back to this directory.
cd scripts/build-windows

rem Now do the changelog:
powershell git describe --abbrev=0 --tags $(git rev-list --tags --skip=1 --max-count=1) > last-tag.txt
cd ../..
gitchangelog > changelog.txt
cd scripts/build-windows

