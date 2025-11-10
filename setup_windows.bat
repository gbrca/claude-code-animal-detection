@echo off
REM Animal Detection App - Windows Setup Script

echo ========================================
echo Animal Detection App - Windows Setup
echo ========================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.11 or 3.12 from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded
echo.

REM Install dependencies
echo [5/5] Installing dependencies...
echo This may take a few minutes...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo Installation FAILED!
    echo ========================================
    echo.
    echo Common solutions:
    echo.
    echo 1. Use Python 3.11 or 3.12 (not 3.13)
    echo    Download: https://www.python.org/downloads/
    echo.
    echo 2. Install Visual C++ Redistributable
    echo    Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo 3. Run this script as Administrator
    echo    Right-click and select "Run as administrator"
    echo.
    echo 4. Try installing packages individually:
    echo    pip install numpy
    echo    pip install opencv-python
    echo    pip install flask
    echo.
    echo See WINDOWS_INSTALL.md for detailed troubleshooting
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation SUCCESSFUL!
echo ========================================
echo.
echo Your animal detection app is ready to use!
echo.
echo Choose an option:
echo   1. Start Web Interface (Recommended)
echo   2. View CLI Help
echo   3. Exit
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting web server...
    echo Open your browser and navigate to: http://localhost:5000
    echo.
    echo Press CTRL+C to stop the server
    echo.
    python src\app.py
) else if "%choice%"=="2" (
    echo.
    python main.py --help
    echo.
    pause
) else (
    echo.
    echo To start the app later:
    echo   1. Open Command Prompt in this folder
    echo   2. Run: venv\Scripts\activate
    echo   3. Run: python src\app.py
    echo.
)

pause
