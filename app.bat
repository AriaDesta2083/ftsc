@echo off
cd /d "%~dp0"
py FTSC.py
if errorlevel 1 (
    python FTSC.py
)
if errorlevel 1 (
    python3 FTSC.py
)
