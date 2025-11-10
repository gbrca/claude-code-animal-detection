# Windows Installation Guide

## Quick Fix for Installation Issues

If you're getting errors during `pip install`, follow these steps:

### Option 1: Use Python 3.11 or 3.12 (Recommended)

Python 3.13 is very new and some packages may not have pre-built wheels yet. For the best experience:

1. **Download Python 3.12**: https://www.python.org/downloads/
2. **During installation**: Check "Add Python to PATH"
3. **Verify installation**:
   ```cmd
   python --version
   ```

### Option 2: Install for Python 3.13

If you want to use Python 3.13, follow these steps:

1. **Update pip first**:
   ```cmd
   python -m pip install --upgrade pip
   ```

2. **Install packages one by one** (to identify issues):
   ```cmd
   pip install numpy
   pip install opencv-python
   pip install flask
   pip install werkzeug
   pip install pillow
   pip install requests
   ```

3. **If OpenCV fails**, try the headless version:
   ```cmd
   pip install opencv-python-headless
   ```

### Option 3: Use Pre-built Wheels

If you're still having issues:

1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/
2. Download pre-built `.whl` files for your Python version
3. Install them:
   ```cmd
   pip install path\to\downloaded\file.whl
   ```

## Complete Setup Instructions for Windows

### Step 1: Create Project Directory
```cmd
cd C:\Users\YourUsername\Documents
git clone YOUR_REPO_URL
cd claude-code-animal-detection
```

### Step 2: Create Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Run the Application

**Web Interface:**
```cmd
python src\app.py
```
Then open browser to: http://localhost:5000

**Command Line:**
```cmd
python main.py path\to\your\image.jpg
```

## Common Windows Issues & Solutions

### Issue 1: "python is not recognized"
**Solution**: Add Python to PATH or use full path:
```cmd
C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\python.exe
```

### Issue 2: OpenCV Import Error
**Solution**: Install Visual C++ Redistributable
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

### Issue 3: Permission Denied
**Solution**: Run Command Prompt as Administrator
- Right-click "Command Prompt"
- Select "Run as administrator"

### Issue 4: Long Path Issues
**Solution**: Enable long paths in Windows:
```cmd
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

### Issue 5: Firewall Blocking Web Server
**Solution**: Allow Python through Windows Firewall
1. Windows Security > Firewall & network protection
2. Allow an app through firewall
3. Add Python

## Alternative: Use Conda (Recommended for Windows)

Conda handles dependencies better on Windows:

1. **Install Miniconda**: https://docs.conda.io/en/latest/miniconda.html

2. **Create environment**:
   ```cmd
   conda create -n animal-detection python=3.12
   conda activate animal-detection
   ```

3. **Install packages**:
   ```cmd
   conda install -c conda-forge opencv
   conda install -c conda-forge flask
   pip install -r requirements.txt
   ```

## Quick Start Script for Windows

Save this as `setup_windows.bat`:

```batch
@echo off
echo ========================================
echo Animal Detection App - Windows Setup
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo Installation failed!
    echo ========================================
    echo.
    echo Try these solutions:
    echo 1. Use Python 3.11 or 3.12 instead of 3.13
    echo 2. Install Visual C++ Redistributable
    echo 3. Run as Administrator
    echo.
    echo See WINDOWS_INSTALL.md for detailed troubleshooting
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start the web interface:
echo   venv\Scripts\activate
echo   python src\app.py
echo.
echo To use CLI:
echo   venv\Scripts\activate
echo   python main.py image.jpg
echo.
pause
```

## Testing Your Installation

After installation, test if everything works:

```cmd
python -c "import cv2; import numpy; import flask; print('All imports successful!')"
```

If you see "All imports successful!", you're ready to go!

## Getting Help

If you're still having issues:

1. Check your Python version: `python --version`
2. Check pip version: `pip --version`
3. Try installing packages individually to find the problem
4. Use Conda instead of pip (often easier on Windows)

## Running the App

Once installed successfully:

```cmd
# Activate environment (every time you open a new terminal)
venv\Scripts\activate

# Start web server
python src\app.py

# Or use CLI
python main.py test_image.jpg
```

Open http://localhost:5000 in your browser!
