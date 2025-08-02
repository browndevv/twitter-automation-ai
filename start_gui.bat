@echo off
title Twitter Automation AI - GUI Launcher
echo.
echo ================================================================
echo  Twitter Automation AI - Modern GUI Interface
echo ================================================================
echo.
echo Starting the graphical user interface...
echo.

cd /d "%~dp0"
python gui\twitter_ai_gui.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start the GUI application
    echo Make sure Python is installed and in your PATH
    echo.
    pause
)
