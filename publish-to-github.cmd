@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 tools\publish_github.py --execute
goto finished
:use_python
where python >nul 2>nul
if errorlevel 1 goto missing_python
python tools\publish_github.py --execute
goto finished
:missing_python
echo Python 3 not found. Please read docs/github-import.md.
:finished
echo.
pause
