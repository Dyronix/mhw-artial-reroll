@echo off
setlocal EnableExtensions

set APP_NAME=MHWildsGogmaziosTracker
set VENV_DIR=.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set DIST_DIR=dist\%APP_NAME%

echo.
echo Building %APP_NAME% for Windows...
echo.

if not exist "%PYTHON_EXE%" (
    echo Creating virtual environment...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv "%VENV_DIR%"
    ) else (
        python -m venv "%VENV_DIR%"
    )
    if errorlevel 1 (
        echo Failed to create virtual environment. Make sure Python is installed on the build machine.
        pause
        exit /b 1
    )
)

echo Installing build dependencies...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 goto :fail
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

if exist "assets\icons\app_icon.png" if not exist "assets\icons\app_icon.ico" (
    echo.
    echo WARNING: assets\icons\app_icon.png exists, but app_icon.ico is missing.
    echo PyInstaller needs assets\icons\app_icon.ico for the EXE icon.
    echo Convert the PNG to ICO before packaging if you want a custom EXE icon.
    echo.
)

echo Running PyInstaller...
"%PYTHON_EXE%" -m PyInstaller --clean --noconfirm packaging\MHWildsGogmaziosTracker.spec
if errorlevel 1 goto :fail

echo Copying distributable data folders...
if not exist "%DIST_DIR%\data" mkdir "%DIST_DIR%\data"
xcopy /E /I /Y "data\config" "%DIST_DIR%\data\config" >nul
if errorlevel 1 goto :fail

if exist "assets" (
    xcopy /E /I /Y "assets" "%DIST_DIR%\assets" >nul
    if errorlevel 1 goto :fail
)

echo.
echo Build complete.
echo Output folder:
echo   %CD%\%DIST_DIR%
echo.
echo Zip the %APP_NAME% folder and send it to users.
pause
exit /b 0

:fail
echo.
echo Build failed. Review the messages above.
pause
exit /b 1
