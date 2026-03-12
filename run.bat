@echo off
setlocal enabledelayedexpansion
title JournalMatch — Starting...

echo.
echo  ================================================
echo    JournalMatch  ^|  Journal Recommendation Tool
echo  ================================================
echo.

REM ── Find Python (tries PATH first, then common install locations) ───────────
set PYTHON=

for %%P in (python py) do (
    if not defined PYTHON (
        %%P --version >nul 2>&1
        if !ERRORLEVEL! == 0 set PYTHON=%%P
    )
)

if not defined PYTHON (
    for %%D in (
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "C:\Python313\python.exe"
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
    ) do (
        if not defined PYTHON (
            if exist %%D set PYTHON=%%D
        )
    )
)

if not defined PYTHON (
    echo  ERROR: Python 3.10 or later was not found on this computer.
    echo.
    echo  Please install Python from:
    echo    https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, tick the box that says:
    echo    "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo  Python found: !PYTHON!
echo.

REM ── Install / verify dependencies ─────────────────────────────────────────
echo  [1/2] Checking dependencies...
echo        (First run downloads ~2 GB of AI libraries — this can take
echo         5-10 minutes. Subsequent runs start in seconds.)
echo.
!PYTHON! -m pip install -r requirements.txt -q --disable-pip-version-check

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo  ERROR: Could not install dependencies.
    echo  Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo  Dependencies ready.
echo.

REM ── Open browser after a short delay ──────────────────────────────────────
start "" cmd /c "timeout /t 6 /noisy >nul && start http://localhost:5000"

REM ── Start the server ───────────────────────────────────────────────────────
echo  [2/2] Starting JournalMatch...
echo.
echo  +--------------------------------------------------+
echo  ^|                                                  ^|
echo  ^|   Your browser will open automatically.          ^|
echo  ^|   If it does not, open:  http://localhost:5000   ^|
echo  ^|                                                  ^|
echo  ^|   To stop the tool, close this window.           ^|
echo  ^|                                                  ^|
echo  +--------------------------------------------------+
echo.

!PYTHON! app.py

pause
