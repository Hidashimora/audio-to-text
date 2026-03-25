@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python launcher ^(py^) not found in PATH.
  echo Install Python 3 and ensure "py" command is available.
  exit /b 1
)

py -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
  echo [ERROR] PyInstaller is not installed.
  echo Run: py -m pip install pyinstaller
  exit /b 1
)

echo Cleaning old build artifacts...
if exist "AudioToText.exe" del /q "AudioToText.exe"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist ".pyi_build" rmdir /s /q ".pyi_build"
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r %%D in (__pycache__) do @if exist "%%D" rmdir /s /q "%%D"
del /s /q "*.spec" >nul 2>nul

echo Starting clean rebuild (onefile)...
py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "AudioToText" ^
  --icon "assets/icons/audio.ico" ^
  --distpath "." ^
  --workpath ".pyi_build" ^
  --add-data "assets;assets" ^
  "main.py"

if errorlevel 1 (
  echo.
  echo [ERROR] Clean rebuild failed.
  exit /b 1
)

echo Cleaning temporary build folders...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist ".pyi_build" rmdir /s /q ".pyi_build"
del /s /q "*.spec" >nul 2>nul

echo.
echo Clean rebuild complete. EXE: AudioToText.exe
exit /b 0
