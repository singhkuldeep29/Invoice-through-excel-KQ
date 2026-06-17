@echo off
setlocal

REM ============================================================
REM  KQ Invoice Generator
REM  Put your Excel (.xlsx) file in this folder, then run this.
REM  Double-click run.bat  OR  type  run.bat  in the terminal.
REM ============================================================

cd /d "%~dp0"

echo.
echo ==========================================
echo   KQ Invoice Generator
echo ==========================================
echo.

REM ---- 1. Find Python -------------------------------------------------
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)

if not defined PY (
    echo ERROR: Python is not installed on this computer.
    echo.
    echo Please install Python first:
    echo   1. Go to:  https://www.python.org/downloads/
    echo   2. Download and run the installer.
    echo   3. IMPORTANT: tick "Add Python to PATH" on the first screen.
    echo   4. After installing, run this file again.
    echo.
    pause
    exit /b 1
)

echo Using Python: %PY%
echo.

REM ---- 2. Install required packages (quiet) --------------------------
echo Checking required packages...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Could not install required packages.
    echo Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

REM ---- 3. Generate the invoices -------------------------------------
echo.
%PY% run_invoices.py
set "RC=%errorlevel%"

echo.
if "%RC%"=="0" (
    echo Finished. Your PDFs are in the "invoices" folder.
    REM open the invoices folder for convenience
    if exist "invoices" start "" "invoices"
) else (
    echo Something went wrong. See the messages above.
)
echo.
pause
endlocal
