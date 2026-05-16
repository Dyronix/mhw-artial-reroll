@echo off
setlocal EnableExtensions EnableDelayedExpansion

set VERSION_FILE=version.txt
set VERSION_FILES=%VERSION_FILE% pyproject.toml src\app\app_info.py packaging\version_info.txt

if "%~1"=="" goto :usage

set BUMP_MAJOR=0
set BUMP_MINOR=0
set BUMP_PATCH=0

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="major" (
    set BUMP_MAJOR=1
) else if /i "%~1"=="minor" (
    set BUMP_MINOR=1
) else if /i "%~1"=="patch" (
    set BUMP_PATCH=1
) else (
    echo Unknown argument: %~1
    echo.
    goto :usage
)
shift
goto :parse_args

:args_done
if not exist "%VERSION_FILE%" (
    echo Missing %VERSION_FILE%.
    exit /b 1
)

set /p CURRENT_VERSION=<"%VERSION_FILE%"
if not defined CURRENT_VERSION (
    echo Failed to read version from %VERSION_FILE%.
    exit /b 1
)

for /f "tokens=1-3 delims=." %%A in ("%CURRENT_VERSION%") do (
    set MAJOR=%%A
    set MINOR=%%B
    set PATCH=%%C
)

if not defined MAJOR goto :bad_version
if not defined MINOR goto :bad_version
if not defined PATCH goto :bad_version

if "%BUMP_MAJOR%"=="1" (
    set /a MAJOR+=1
    set MINOR=0
    set PATCH=0
)

if "%BUMP_MINOR%"=="1" (
    set /a MINOR+=1
    set PATCH=0
)

if "%BUMP_PATCH%"=="1" (
    set /a PATCH+=1
)

set NEW_VERSION=%MAJOR%.%MINOR%.%PATCH%
set TAG_NAME=v%NEW_VERSION%

echo Current version: %CURRENT_VERSION%
echo New version:     %NEW_VERSION%
echo Tag:             %TAG_NAME%
echo.

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
    echo This script must be run from inside the git repository.
    exit /b 1
)

git diff --quiet -- %VERSION_FILES%
if errorlevel 1 (
    echo One or more version files already have unstaged changes.
    echo Commit or stash those changes before bumping the version.
    exit /b 1
)

git diff --cached --quiet -- %VERSION_FILES%
if errorlevel 1 (
    echo One or more version files already have staged changes.
    echo Commit or unstage those changes before bumping the version.
    exit /b 1
)

git rev-parse -q --verify "refs/tags/%TAG_NAME%" >nul 2>nul
if not errorlevel 1 (
    echo Tag %TAG_NAME% already exists.
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference = 'Stop';" ^
    "$version = '%NEW_VERSION%';" ^
    "$dq = [char]34;" ^
    "Set-Content 'version.txt' $version -NoNewline -Encoding ASCII;" ^
    "$pyproject = Get-Content 'pyproject.toml' -Raw;" ^
    "$pyproject = $pyproject -replace ('(?m)^version = ' + $dq + '[^' + $dq + ']+' + $dq), ('version = ' + $dq + $version + $dq);" ^
    "Set-Content 'pyproject.toml' $pyproject -NoNewline -Encoding ASCII;" ^
    "$appInfo = Get-Content 'src/app/app_info.py' -Raw;" ^
    "$appInfo = $appInfo -replace ('APP_VERSION = ' + $dq + '[^' + $dq + ']+' + $dq), ('APP_VERSION = ' + $dq + $version + $dq);" ^
    "Set-Content 'src/app/app_info.py' $appInfo -NoNewline -Encoding ASCII;" ^
    "$vi = Get-Content 'packaging/version_info.txt' -Raw;" ^
    "$parts = $version.Split('.');" ^
    "$tuple = '(' + $parts[0] + ', ' + $parts[1] + ', ' + $parts[2] + ', 0)';" ^
    "$vi = $vi -replace 'filevers=\([0-9]+, [0-9]+, [0-9]+, 0\)', ('filevers=' + $tuple);" ^
    "$vi = $vi -replace 'prodvers=\([0-9]+, [0-9]+, [0-9]+, 0\)', ('prodvers=' + $tuple);" ^
    "$vi = $vi -replace 'StringStruct\(''FileVersion'', ''[^'']+''\)', ('StringStruct(''FileVersion'', ''' + $version + ''')');" ^
    "$vi = $vi -replace 'StringStruct\(''ProductVersion'', ''[^'']+''\)', ('StringStruct(''ProductVersion'', ''' + $version + ''')');" ^
    "Set-Content 'packaging/version_info.txt' $vi -NoNewline -Encoding ASCII;"
if errorlevel 1 (
    echo Failed to update version files.
    exit /b 1
)

git add %VERSION_FILES%
if errorlevel 1 (
    echo Failed to stage version files.
    exit /b 1
)

git commit -m "Bump version to %NEW_VERSION%"
if errorlevel 1 (
    echo Failed to create version bump commit.
    exit /b 1
)

git tag "%TAG_NAME%"
if errorlevel 1 (
    echo Failed to create tag %TAG_NAME%.
    exit /b 1
)

echo.
echo Created version bump commit and tag %TAG_NAME%.
echo Push with:
echo   git push
echo   git push origin %TAG_NAME%
exit /b 0

:bad_version
echo Version "%CURRENT_VERSION%" is not in major.minor.patch format.
exit /b 1

:usage
echo Usage: %~nx0 major [minor] [patch]
echo        %~nx0 minor [patch]
echo        %~nx0 patch
echo.
echo Examples:
echo   %~nx0 patch       bumps 0.2.1 to 0.2.2
echo   %~nx0 minor       bumps 0.2.1 to 0.3.0
echo   %~nx0 major       bumps 0.2.1 to 1.0.0
echo   %~nx0 major minor bumps 0.2.1 to 1.1.0
exit /b 1
