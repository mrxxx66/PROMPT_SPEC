@echo off
REM Script to download Dobby library for Windows

echo Creating external directory...
if not exist jni\external mkdir jni\external

echo Downloading Dobby library...
echo Note: You need to manually download Dobby from:
echo https://github.com/jmpews/Dobby/releases
echo.
echo Download the Windows version and extract libdobby.a to jni\external\
echo.
echo Alternatively, build Dobby from source using the NDK.
pause