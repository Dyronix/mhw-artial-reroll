@echo off
setlocal EnableExtensions

echo Cleaning generated build files...

if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist

for /d /r %%D in (__pycache__) do (
    if exist "%%D" rmdir /S /Q "%%D"
)

del /Q *.spec 2>nul
del /Q *.log 2>nul

echo Clean complete.
pause
